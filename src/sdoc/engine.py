#!/usr/bin/env python
# encoding=utf8 ---------------------------------------------------------------
# Project           : NAME
# -----------------------------------------------------------------------------
# Author            : FFunction
# License           : BSD License
# -----------------------------------------------------------------------------
# Creation date     : YYYY-MM-DD
# Last modification : YYYY-MM-DD
# -----------------------------------------------------------------------------

from __future__ import print_function

VERSION = "0.0.0"
LICENSE = "http://ffctn.com/doc/licenses/bsd"

import re, sys
import texto.core, texto.blocks, texto.texto2html
import pamela.web

PROCESSORS = pamela.web.getProcessors()

# -----------------------------------------------------------------------------
#
# EMBED BLOCK PARSER
#
# -----------------------------------------------------------------------------

class EmbedBlockParser( texto.blocks.BlockParser ):

	RE_START = re.compile("^\[embed:(\w+)\]$", re.MULTILINE)
	RE_END   = re.compile("^\[end\]$", re.MULTILINE)

	WRAPPERS = {
		"text/plain"       : lambda _:"<pre>{0}</pre>".format(_),
		"text/html"        : lambda _:"<div class='embed'>{0}</div>".format(_),
		"text/javascript"  : lambda _:"<script type='text/javascript'>{0}</script>".format(_),
	}

	def recognises( self, context ):
		match = self.RE_START.match(context.currentFragment())
		if match:
			end_match = self.RE_END.search(context.documentText, context.getOffset())
			if match and end_match:
				return (match, end_match)
		return None

	def process( self, context, match):
		start_match, end_match = match
		embed_type             = start_match.group(1)
		embed_content          = context.fragment(start_match.end() + context.getOffset(), end_match.start())
		embed_element          = context.document.createElementNS(None, "Embed")
		embed_element.appendChild(context.document.createTextNode(self._processContent(embed_type, embed_content)))
		context.currentNode.appendChild(embed_element)
		# We update the current block and the current offset
		context.setOffset(end_match.end())
		context.setCurrentBlock(start_match.start() + context.getOffset(), end_match.end())

	def _processContent( self, type, text ):
		assert type in PROCESSORS
		content, content_type = PROCESSORS[type](text, None)
		wrapper = self.WRAPPERS.get(content_type)
		return wrapper(content) if wrapper else content

# -----------------------------------------------------------------------------
#
# PARSER
#
# -----------------------------------------------------------------------------

class Parser( texto.core.Parser ):

	def createBlockParsers( self ):
		texto.core.Parser.createBlockParsers(self)
		self.blockParsers.append(EmbedBlockParser())

# -----------------------------------------------------------------------------
#
# PROCESSOR
#
# -----------------------------------------------------------------------------

class Processor( texto.texto2html.Processor ):

	def on_Embed( self, element ):
		return "EMBED:" + "\n".join(_.data for _ in element.childNodes)  + ":EMBED"

# -----------------------------------------------------------------------------
#
# OPERATIONS
#
# -----------------------------------------------------------------------------

def parse( text, asXML=False, output=None ):
	parser    = Parser()
	document  = parser.parse(text).document
	if asXML:
		result = document.toprettyxml("  ").encode("utf8")
	else:
		processor = Processor()
		result    = processor.generate(document)
	if output: output.write(result)
	return result

def parsePath( path ):
	with open(path) as f:
		return parse(f.read())

# -----------------------------------------------------------------------------
#
# MAIN
#
# -----------------------------------------------------------------------------

if __name__ == "__main__":
	for a in sys.argv[1:]:
		print (parsePath(a).encode("utf-8"))

# EOF - vim: ts=4 sw=4 noet
