#!/usr/bin/env python
# encoding=utf8 ---------------------------------------------------------------
# Project           : smalldoc
# -----------------------------------------------------------------------------
# Author            : FFunction
# License           : BSD License
# -----------------------------------------------------------------------------
# Creation date     : 2016-12-09
# Last modification : 2016-12-09
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

	def parsePath( self, path ):
		program    = sugar.main.run(["-clnone", "-Llib/sjs", path])
		for module in program.getModules():
			if module.isImported(): continue
			self.onModule(module)

	def onModule( self, model ):
		e = self.documenter.createModule(name=model.getName(), id=self._getID(model))
		# TODO: Add dependencies
		# TODO: Add source offsets
		return self.documenter.addElement(self._setSlots(model, e))

	def onFunction( self, model ):
		e = self.documenter.createFunction(name=model.getName(), id=self._getID(model), tags=self._getTags(model))
		# TODO: Add parameters and return value
		# TODO: Add source offsets
		return self._setSlots(model, e)

	def onClass( self, model ):
		e = self.documenter.createClass(name=model.getName(), id=self._getID(model), tags=self._getTags(model))
		# TODO: Add parent relations
		# TODO: Add inherited slots
		# TODO: Add source offsets
		return self._setSlots(model, e)

	def onValue( self, model ):
		# TODO: Add value
		# TODO: Add source offsets
		return self.documenter.createElement(name=model.getName(), id=self._getID(model), tags=self._getTags(model), type=KEY_VALUE)

	# =========================================================================
	# HELPERS
	# =========================================================================

	def on( self, model ):
		if isinstance(model, IFunction):
			return self.onFunction(model)
		elif isinstance(model, IClass):
			return self.onClass(model)
		elif isinstance(model, IAttribute):
			return self.onValue(model)
		elif isinstance(model, IImportOperation):
			pass
		else:
			raise Exception("Type not supported: {0}".format(model))

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

if __name__ == "__main__":
	import sys, json
	import smalldoc.model
	d = SugarDriver(smalldoc.model.Documenter())
	d.parsePath(sys.argv[1])
	print (json.dumps(d.toJSON()))

# EOF - vim: ts=4 sw=4 noet
