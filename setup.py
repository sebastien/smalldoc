#!/usr/bin/env python
# Encoding: utf8
# -----------------------------------------------------------------------------
# Project   : Smalldoc - Python Documentation introspection
# -----------------------------------------------------------------------------
# Author    : Sebastien Pierre                     <sebastien.pierre@gmail.com>
# License   : Revised BSD License
# -----------------------------------------------------------------------------
# Creation  : 03-Avr-2006
# Last mod  : 02-Dec-2016
# -----------------------------------------------------------------------------

import sys
from distutils.core import setup

SUMMARY     = "SmallTalk-like Python API documenter"

VERSION      = "0.5.9"
DESCRIPTION = """\
Smalldoc produces an interactive, JavaScript-based API documentation that resembles
to the way class navigation is made in SmallTalk. Smalldoc page design is loosely
inspired from Io language documentation page
<http://www.iolanguage.com/docs/reference/browser.cgi>, which initially inspired
the projet.\

"""
# ------------------------------------------------------------------------------
#
# SETUP DECLARATION
#
# ------------------------------------------------------------------------------

setup(
	name         = "smalldoc",
	version      = VERSION,
	author       = "Sebastien Pierre", author_email = "sebastien.pierre@gmail.com",
	description   = SUMMARY, long_description  = DESCRIPTION,
	license      = "Revised BSD License",
	keywords     = "API, documentation, generator, html, javascript",
	url          = "http://www.github.com/sebastien/smalldoc",
	package_dir  = { "": "src" },
	packages     = ["smalldoc"],
	package_data = {"smalldoc":["src/smalldoc/smalldoc.tmpl"] },
	scripts      = ["bin/smalldoc"]
)

# EOF - vim: tw=80 ts=4 sw=4 noet
