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

import xml

KEY_MODULE          = "module"
KEY_CLASS           = "class"
KEY_FUNCTION        = "function"
KEY_METHOD          = "method"
KEY_CONSTRUCTOR     = "constructor"
KEY_CLASS_METHOD    = "class method"
KEY_CLASS_ATTRIBUTE = "class attribute"
KEY_ATTRIBUTE       = "attribute"
KEY_VALUE           = "value"
KEY_PARENT          = "parent"

MOD_INHERITED       = "inherited"

REL_SLOT            = "slot"
REL_EXTENDS         = "extends"

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

	def __init__( self, id=None, name=None, type=None, parent=None, documentation=None, source=None, range=None ):
		self.id            = id
		self.name          = name
		self.type          = type
		self.parent        = parent
		self.documentation = documentation
		self.source        = source
		self.range         = range
		self.children      = []
		self.relations     = []

	def addRelation( self, verb, subject, object ):
		self.relations.append((verb, subject, object))

	def setSlot( self, name, value ):
		self.children.append((name, value))
		return self

	def setName( self, name ):
		self.name = name
		return self

	def addChild( self, name, element ):
		self.children.append((name, element))
		return self

	def setDocumentation( self, text ):
		self.documentation = text
		return self

	def toJSON( self ):
		return dict((k,v) for k,v in dict(
			id            = self.id,
			name          = self.name,
			type          = self.type,
			parent        = self.parent.id if self.parent else None,
			documentation = self.documentation,
			source        = self.source,
			range         = self.range,
			children      = [(
				_[0],
				_[1].toJSON() if isinstance(_[1],Element) else _[1],
			) for _ in self.children or () ],
			relations     = [(
				_[0],
				_[1].id if isinstance(_[1],Element) else _[1],
				_[2].id if isinstance(_[2],Element) else _[2]
			) for _ in self.relations or ()]
		).items() if v)

	def toXML( self ):
		node = document.createElement("element")
		node.setAttribute("id",   self.id)
		node.setAttribute("name", self.nam)
		if self.type: node.setAttribute("type", self.type)

# -----------------------------------------------------------------------------
#
# DOCUMENTER
#
# -----------------------------------------------------------------------------

class Documenter(object):

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

# EOF - vim: ts=4 sw=4 noet
