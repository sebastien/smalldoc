#!/usr/bin/env python
# Encoding: iso-8859-1
# vim: tw=80 ts=4 sw=4 noet
# -----------------------------------------------------------------------------
# Project   : SDoc - Python Documentation introspection
# -----------------------------------------------------------------------------
# Author    : Sebastien Pierre                               <sebastien@ivy.fr>
# License   : Revised BSD License
# -----------------------------------------------------------------------------
# Creation  : 03-Avr-2006
# Last mod  : 03-Avr-2006
# History   :
#             03-Avr-2006 - First implementation
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
    name         = "SDoc",
    version      = main.__version__,

    author       = "Sebastien Pierre", author_email = "sebastien@ivy.fr",
    description   = SUMMARY, long_description  = DESCRIPTION,
    license      = "Revised BSD License",
    keywords     = "API, documentation, generator, html, javascript",
    url          = "http://www.ivy.fr/sdoc",
    package_dir  = { "": "Sources" },
    packages     = ["sdoc"],
    package_data = { "sdoc": ["*.tmpl"] },
    scripts      = ["Scripts/sdoc"]
)

# EOF
