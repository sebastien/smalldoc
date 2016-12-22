#!/usr/bin/env python
# encoding=utf8 ---------------------------------------------------------------
# Project           : smalldoc
# -----------------------------------------------------------------------------
# Author            : FFunction
# License           : BSD License
# -----------------------------------------------------------------------------
# Creation date     : 2016-12-09
# Last modification : 2016-12-20
# -----------------------------------------------------------------------------

from __future__ import print_function

import sugar.main
from lambdafactory.interfaces import *
from smalldoc.drivers import Driver
from smalldoc.model   import *

__doc__ = """
Defines the driver for extracting documentation information from
Sugar source files.
"""

class SugarDriver(Driver):
	"""Parses Sugar source files and generates the smalldoc model."""

	def parse( self, path ):
		# TODO: Parse a module
		return self.parsePath(path)

	def parsePath( self, path ):
		program    = sugar.main.run(["-clnone", "-Llib/sjs", "-Lsrc/sjs"] + ["-L" + _ for _ in self.path or ()] + [path])
		for module in program.getModules():
			if module.isImported(): continue
			self.onModule(module)

	def onModule( self, model ):
		e = self.documenter.createModule(
			name=model.getName(),
			id=self._getID(model),
			documentation=self._getDocumentation(model)
		)
		# TODO: Add dependencies
		# TODO: Add source offsets
		return self.documenter.addElement(self._setSlots(model, e))

	def onFunction( self, model ):
		e = self.documenter.createFunction(
			name=model.getName(),
			id=self._getID(model),
			tags=self._getTags(model),
			documentation=self._getDocumentation(model),
		)
		args = []
		for arg in model.getArguments():
			a = arg.getName()
			if arg.getTypeDescription(): a += ":" + arg.getTypeDescription()
			# FIXME: Should translate the value back to Sugar
			if arg.isOptional(): a+="="+str(arg.getDefaultValue())
			if arg.isRest(): a+="..."
			if arg.isKeywordsRest(): a+="=..."
			args.append(a)
		e.addRelation(REL_ARGUMENTS, args)
		a = "".join("<span class='argument'>" + _ + "</span>" for _ in args)
		r = "<span class='name'>{0}</span><span class='arguments'>{1}</span>".format(model.getName(), a)
		e.representation = r
		# TODO: Add parameters and return value
		# TODO: Add source offsets
		return self._setSlots(model, e)

	def onClass( self, model ):
		e = self.documenter.createClass(
			name=model.getName(),
			id=self._getID(model),
			tags=self._getTags(model),
			documentation=self._getDocumentation(model),
		)
		# TODO: Add parent relations
		# TODO: Add inherited slots
		# TODO: Add source offsets
		return self._setSlots(model, e)

	def onValue( self, model ):
		# TODO: Add value
		# TODO: Add source offsets
		value = model.getDefaultValue()

		return self.documenter.createElement(
			name=model.getName(),
			id=self._getID(model),
			tags=self._getTags(model),
			type=KEY_VALUE,
			documentation=self._getDocumentation(model),
			representation=self._getRepresentation(value)
		)

	# =========================================================================
	# HELPERS
	# =========================================================================

	def on( self, model ):
		if isinstance(model, IFunction) or isinstance(model, IClassMethod) or isinstance(model, IMethod):
			res = self.onFunction(model)
		elif isinstance(model, IClass):
			res = self.onClass(model)
		elif isinstance(model, IAttribute):
			res = self.onValue(model)
		elif isinstance(model, IImportOperation):
			pass
		else:
			raise Exception("Type not supported: {0}".format(model))
		if res and model and model.sourceLocation:
			s,e,p = model.sourceLocation
			res.addRelation(REL_SOURCE, p, [s,e])
		return res

	def _getID( self, model ):
		"""Generates the fully qualified name for the given LambdaFactory model
		element."""
		return ".".join([_.getName() for _ in self.scopes] + [model.getName()])

	def _setSlots( self, model, element ):
		self.scopes.append(model)
		for name, value in model.getSlots():
			element.setSlot(name, self.on(value))
		self.scopes.pop()
		return element

	def _getDocumentation( self, model, markup="texto" ):
		doc = model.getDocumentation()
		if doc:
			return self.render(doc.getContent(), markup)
		else:
			return None

	def _getRepresentation( self, model ):
		if model and model.sourceLocation:
			s,e,p = model.sourceLocation
			return self.unindent(self.readSource(p,s,e)) if p!=-1 else None
		else:
			return None

	def _getTags( self, model ):
		res = []
		if   isinstance(model, IClassAttribute): res.append(KEY_CLASS_ATTRIBUTE)
		if   isinstance(model, IConstructor):    res.append(KEY_CONSTRUCTOR)
		elif isinstance(model, IClassMethod):    res.append(KEY_CLASS_METHOD)
		elif isinstance(model, IMethod):         res.append(KEY_METHOD)
		elif isinstance(model, IFunction):       res.append(KEY_FUNCTION)
		if   isinstance(model, INumber):         res.append(KEY_NUMBER)
		if   isinstance(model, IString):         res.append(KEY_STRING)
		if   isinstance(model, IList):           res.append(KEY_LIST)
		if   isinstance(model, IDict):           res.append(KEY_MAP)
		if   isinstance(model, IReference):      res.append(KEY_REFERENCE)
		return res

# EOF - vim: ts=4 sw=4 noet
