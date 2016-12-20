#!/usr/bin/env python
# encoding=utf8 ---------------------------------------------------------------
# Project           : smalldoc
# -----------------------------------------------------------------------------
# Author            : FFunction
# License           : BSD License
# -----------------------------------------------------------------------------
# Creation date     : 2016-12-20
# Last modification : 2016-12-20
# -----------------------------------------------------------------------------

from __future__ import print_function

import texto.main, texto.parser
from   texto.formats.html import Processor
from smalldoc.drivers import Driver
from smalldoc.model   import *

__doc__ = """
Defines the driver for extracting documentation information from
Sugar source files.
"""

class TextoProcessor(Processor):

	def __init__( self, driver, *args, **kwargs ):
		Processor.__init__(self, *args, **kwargs)
		self.driver   = driver
		self.context  = []
		self.sections = []

	def on_Document( self, element ):
		#title = self.text(self.first(element, "Header/Title/title"))
		e     = self.driver.documenter.createElement(
			id            = self.driver._documentName,
			type          = KEY_DOCUMENT,
			name          = self.driver._documentName,
			source        = self.driver._documentPath,
			tags          = ["texto"]
		)
		self.context.append(e)
		html  = Processor.on_Document(self, element)
		e.documentation = html
		self._setLocation(e, element)
		self.context.pop()
		self.driver.documenter.addElement(e)
	 	return html

	# def on_Header( self, element ):
	# 	pass

	def on_Section( self, element ):
		name = self.text(self.first(element, "Heading"))
		e     = self.driver.documenter.createElement(
			id            = self.driver._documentName + "." + element.getAttribute("id"),
			type          = KEY_SECTION,
			name          = name,
			source        = self.driver._documentPath,
		)
		self.context[-1].setSlot(name, e)
		self.context.append(e)
		html = Processor.on_Section(self, element)
		e.documentation = html
		self._setLocation(e, element)
		self.context.pop()
		if self.sections:
			last = self.sections[-1]
			last.addRelation(REL_NEXT, e)
			e.addRelation(REL_PREVIOUS, last)
		self.sections.append(e)
		return html

	def _setLocation( self, model, element ):
		start = element.getAttribute("_start")
		end   = element.getAttribute("_end")
		model.addRelation(REL_SOURCE, self.driver._documentPath, [start, end])

class TextoDriver(Driver):
	"""Parses Texto source files and generates the corresponding model."""

	def init( self ):
		self.processor    = TextoProcessor(self)
		self._documentName = None
		self._documentPath = None

	def parse( self, name ):
		if not os.path.exists(name):
			raise ValueError
		else:
			return self.parsePath(name)

	def parsePath( self, path ):
		parser = texto.parser.Parser(os.path.dirname(path))
		self._documentName = os.path.basename(path).rsplit(".")[0]
		self._documentPath = path
		with open(path) as f: text = f.read()
		context = parser.parse(text, offsets=False)
		result = self.processor.generate(context.document, True, {})

	# DOCUMENT: Full docstring
	# DEFINE: sections, tables, links, terms

# EOF - vim: ts=4 sw=4 noet
