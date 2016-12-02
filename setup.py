#!/usr/bin/env python
# Encoding: utf8
# -----------------------------------------------------------------------------
# Project   : SDoc - Python Documentation introspection
# -----------------------------------------------------------------------------
# Author    : Sebastien Pierre                    <sebastien.pierrei@gmail.com>
# License   : Revised BSD License
# -----------------------------------------------------------------------------
# Creation  : 03-Avr-2006
# Last mod  : 02-Dec-2016
# -----------------------------------------------------------------------------

import sys ; sys.path.insert(0, "Sources")
import sdoc.main as main
from distutils.core import setup

SUMMARY     = "SmallTalk-like Python API documenter"

DESCRIPTION = """\
SDoc produces an interactive, JavaScript-based API documentation that resembles
to the way class navigation is made in SmallTalk. SDoc page design is loosely
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
	name         = "sdoc",
	version      = main.__version__,
	author       = "Sebastien Pierre", author_email = "sebastien@ivy.fr",
	description   = SUMMARY, long_description  = DESCRIPTION,
	license      = "Revised BSD License",
	keywords     = "API, documentation, generator, html, javascript",
	url          = "http://www.github.com/sebastien/sdoc",
	package_dir  = { "": "src" },
	packages     = ["sdoc"],
	package_data = { "sdoc": ["*.tmpl"] },
	scripts      = ["bin/sdoc"]
)

# EOF - vim: tw=80 ts=4 sw=4 noet
