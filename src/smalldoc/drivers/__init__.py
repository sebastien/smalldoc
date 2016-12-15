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

try:
	import texto.parser, texto.main
except ImportError as e:
	texto = None

class Driver(object):

	def __init__( self, documenter, path=() ):
		self.documenter = documenter
		self.scopes     = []
		self.path       = path

	def render( self, text, markup ):
		if markup == "texto":
			first_line_indent = texto.parser.Parser.getIndentation(text[:text.find("\n")])
			text_indent = texto.parser.Parser.getIndentation(text)
			text = " " * (text_indent - first_line_indent) + text
			return texto.main.text2htmlbody(text.decode("utf8"))
		else:
			raise NotImplementedError

	def toJSON( self ):
		return self.documenter.toJSON()

# EOF - vim: ts=4 sw=4 noet
