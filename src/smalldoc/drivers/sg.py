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

class SugarDriver(Driver):

	def parsePath( self, path ):
		program    = sugar.main.run(["-clnone", "-Llib/sjs", path])
		for module in program.getModules():
			if module.isImported(): continue
			self.onModule(module)

	def onModule( self, model ):
		e = self.documenter.createFunction(name=model.getName(), id=self._getID(model))
		return self.documenter.addElement(self._setSlots(model, e))

	def onFunction( self, model ):
		e = self.documenter.createFunction(name=model.getName(), id=self._getID(model))
		return self._setSlots(model, e)

	def onClass( self, model ):
		e = self.documenter.createClass(name=model.getName(), id=self._getID(model))
		return self._setSlots(model, e)

	def onValue( self, model ):
		return self.documenter.createElement()

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
		return ".".join([_.getName() for _ in self.scopes] + [model.getName()])

	def _setSlots( self, model, element ):
		self.scopes.append(model)
		for name, value in model.getSlots():
			element.setSlot(name, self.on(value))
		self.scopes.pop()
		return element

if __name__ == "__main__":
	import sys, json
	import smalldoc.model
	d = SugarDriver(smalldoc.model.Documenter())
	d.parsePath(sys.argv[1])
	print (json.dumps(d.toJSON()))

# EOF - vim: ts=4 sw=4 noet
