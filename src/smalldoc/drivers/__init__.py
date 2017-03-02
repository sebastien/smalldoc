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

import re
from   functools import reduce

try:
	import texto.parser, texto.main
except ImportError as e:
	texto = None

RE_INDENT = re.compile("^([\t ]*)")

class Driver(object):

	def __init__( self, documenter, path=(), logger=None ):
		self.documenter = documenter
		self.scopes     = []
		self.path       = path
		self._sources   = {}
		self.logger     = logger
		self.init()

	def info( self, *message ):
		if self.logger: self.logger.info(*message)

	def warn( self, *message ):
		if self.logger: self.logger.warn(*message)

	def error( self, *message ):
		if self.logger: self.logger.error(*message)

	def init( self ):
		pass

	def parse( self, name ):
		"""Parses the given path or module name."""
		raise NotImplementedError

	def readSource( self, path, start=None, end=None):
		text = self._sources.get(path)
		if path not in self._sources:
			with open(path) as f:
				text = f.read()
				self._sources[path] = text
		if start is None and end is None:
			return text
		elif start is None:
			return text[:end]
		else:
			return text[start:end]

	def render( self, text, markup ):
		if markup == "texto":
			first_line_indent = texto.parser.Parser.getIndentation(text[:text.find("\n")])
			text_indent = texto.parser.Parser.getIndentation(text)
			text = " " * (text_indent - first_line_indent) + text
			return texto.main.text2htmlbody(text)
		else:
			raise NotImplementedError

	def toJSON( self ):
		return self.documenter.toJSON()

	def _getLineIndent( self, line, match=None ):
		return (match or RE_INDENT.match(line)).group().replace("\t", " ")

	def _getLinesIndent( self, lines ):
		indent = [len(self._getLineIndent(_)) for _ in lines]
		if   len(indent) == 0:
			return 0
		elif len(indent) == 1:
			return indent[0]
		else:
			return reduce(min, indent[1:])

	def _reindentLine( self, line, delta ):
		indent = RE_INDENT.match(line).group()
		i      = 0
		while delta > 0 and indent:
			if indent[0] == '\t':
				delta -= 4
			else:
				delta -= 1
			i += 1
		return line[i:]

	def unindent( self, text ):
		lines  = text.split("\n")
		indent = self._getLinesIndent(lines)
		return "\n".join(self._reindentLine(_, indent) for _ in lines)

# EOF - vim: ts=4 sw=4 noet
