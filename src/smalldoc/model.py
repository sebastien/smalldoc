#!/usr/bin/env python
# encoding=utf8 ---------------------------------------------------------------
# Project           : smalldoc
# -----------------------------------------------------------------------------
# Author            : FFunction
# License           : BSD License
# -----------------------------------------------------------------------------
# Creation date     : 2016-12-09
# Last modification : 2016-12-15
# -----------------------------------------------------------------------------

import os, json

KEY_MODULE          = "module"
KEY_CLASS           = "class"
KEY_FUNCTION        = "function"
KEY_METHOD          = "method"
KEY_CONSTRUCTOR     = "class constructor"
KEY_CLASS_METHOD    = "class method"
KEY_CLASS_ATTRIBUTE = "class attribute"
KEY_ATTRIBUTE       = "attribute"
KEY_VALUE           = "value"
KEY_PARENT          = "parent"
KEY_STRING          = "string"
KEY_NUMBER          = "number"
KEY_MAP             = "map"
KEY_LIST            = "list"
KEY_VALUE           = "value"
KEY_REFERENCE       = "reference"

MOD_INHERITED       = "inherited"

REL_EXTENDS         = "extends"
REL_ARGUMENTS       = "arguments"
REL_SLOT            = "defines"
REL_DEFINED         = "defined"

KEYS_ORDER = (
	KEY_PARENT,
	KEY_MODULE,
	KEY_CLASS,
	KEY_CONSTRUCTOR,
	KEY_CLASS_ATTRIBUTE,
	KEY_CLASS_METHOD,
	KEY_ATTRIBUTE,
	KEY_METHOD,
	KEY_FUNCTION,
	KEY_VALUE
)

SPECIAL_ATTRIBUTES = {
	"__init__"    : "constructor",
	"__cmp__"     : "compare to",
	"__eq__"      : "equals",
	"__del__"     : "delete",
	"__getitem__" : "get item",
	"__setitem__" : "set item",
	"__len__"     : "length",
	"__iter__"    : "iterator",
	"__call__"    : "when invoked",
	"__str__"     : "string conversion",
	"__repr__"    : "string repr",
	"__bases__"   : lambda _: ", ".join(c.__name__ for c in _)
}

COMPACT_NAMES = {
	"container"     : "cr",
	"documented"    : "d",
	"description"   : "de",
	"docstring"     : "ds",
	"group"         : "g",
	"name"          : "n",
	"representation": "re",
	"root"          : "ro",
	"title"         : "t",
	"undocumented"  : "u"
}


# -----------------------------------------------------------------------------
#
# ELEMENT
#
# -----------------------------------------------------------------------------

class Element(object):
	"""Smalldoc's *element* represents a generic/versatile class to represent
	program element. There should be no need to subclass the element, as it
	is meant to encapsulate the important information that is required
	to display an element of a program.

	Its properties and API were carefully selected in order to avoid having
	to create one subclass per type, and make sure the data could be
	serialized to a consistent JSON format that can be easily processed
	using JavaScript."""

	def __init__( self, id=None, name=None, type=None, parent=None, tags=None, documentation=None, representation=None, source=None, range=None ):
		self.id             = id
		self.name           = name
		self.type           = type
		self.tags           = tags
		self.parent         = parent
		self.documentation  = documentation
		self.representation = representation
		self.source         = source
		self.range          = range
		self.children       = []
		self.relations      = []

	def addRelation( self, verb, *objects ):
		self.relations.append([verb] + list(objects))
		return self

	def setSlot( self, name, value ):
		self.children.append((name, value))
		value.addRelation(REL_DEFINED, self)
		value.addRelation(REL_SLOT, name, value)
		return self

	def addChild( self, name, element ):
		self.children.append((name, element))
		return self

	def toJSON( self ):
		return dict((k,v) for k,v in dict(
			id             = self.id,
			name           = self.name,
			type           = self.type,
			tags           = self.tags,
			parent         = self.parent.id if self.parent else None,
			documentation  = self.documentation,
			representation = self.representation,
			source         = self.source,
			range          = self.range,
			children       = [(
				_[0],
				_[1].toJSON() if isinstance(_[1],Element) else _[1],
			) for _ in self.children or () ],
			relations     = [[
				_.id if isinstance(_,Element) else _ for _ in r
			] for r in self.relations or ()]
		).items() if v)

# -----------------------------------------------------------------------------
#
# DOCUMENTER
#
# -----------------------------------------------------------------------------

class Documenter(object):
	"""A factory-like abstraction to create elements. Documenters are
	wrapped by drivers, which create elements based on a given input."""

	def __init__( self ):
		self.elements = []

	def addElement( self, element ):
		assert isinstance(element, Element)
		self.elements.append(element)
		return element

	def createElement( self, **kwargs ):
		return Element(**kwargs)

	def createModule( self, name, **kwargs):
		return self.createElement(type=KEY_MODULE, **kwargs)

	def createFunction( self, name, **kwargs):
		return self.createElement(type=KEY_FUNCTION, **kwargs)

	def createClass( self, name, **kwargs):
		return self.createElement(type=KEY_CLASS, **kwargs)

	def toJSON( self ):
		return {"children":[[_.name or _.id, _.toJSON()] for _ in self.elements]}

	def toHTML( self ):
		return {"children":[[_.name or _.id, _.toJSON()] for _ in self.elements]}

	def write( self, stream, format ):
		templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
		if format == "json":
			json.dump(self.toJSON(), stream)
		elif format == "html":
			with open(os.path.join(templates, "html-5.0.9.js")) as f: jsh  = f.read()
			with open(os.path.join(templates, "smalldoc.js"))   as f: jss  = f.read()
			with open(os.path.join(templates, "smalldoc.css"))  as f: css  = f.read()
			with open(os.path.join(templates, "smalldoc.html")) as f: html = f.read()
			data = json.dumps(self.toJSON())
			html = html.replace('<link href="smalldoc.css" rel="stylesheet" />', "<style>" + css + "</style>")
			html = html.replace(' src="html-5.0.9.js">', ">" + jsh)
			html = html.replace(' src="smalldoc.js">',   ">" + jss + ";smalldoc.setup(" + data + ");")
			html = html.replace('data-url="data.json"', "")
			stream.write(html)
		elif format == "js":
			js  = ""
			js += "smalldoc.DATA=" + json.dumps(self.toJSON()) + ";"
			with open(os.path.join(templates, "html-5.0.9.js")) as f: js += f.read()
			with open(os.path.join(templates, "smalldoc.js"))   as f: js += f.read()
			js += "smalldoc.loadCSS();smalldoc.load('api.json');smalldoc.setup();"
			stream.write(js)

# EOF - vim: ts=4 sw=4 noet
