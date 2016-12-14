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

class Driver(object):

	def __init__( self, documenter ):
		self.documenter = documenter
		self.scopes     = []

	def toJSON( self ):
		return self.documenter.toJSON()

# EOF - vim: ts=4 sw=4 noet
