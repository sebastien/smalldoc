#!/usr/bin/env python
# Encoding: iso-8859-1
# vim: tw=80 ts=4 sw=4 noet
# -----------------------------------------------------------------------------
# Project   : Smalldoc - Python Documentation introspection
# -----------------------------------------------------------------------------
# Author    : Sebastien Pierre                               <sebastien@ivy.fr>
# License   : Revised BSD License
# -----------------------------------------------------------------------------
# Creation  : 2006-04-30
# Last mod  : 2016-12-08
# -----------------------------------------------------------------------------

# FIXME: Does not seem to work well with multiple inheritance/interfaces
# inheritance

# TODO: Support for decorators "_decorated" attribute (so that we are not
# displayed a "decorator"
# TODO: Optimize by using a StringIO instead of concateating strings
# TODO: Use paths and not the 'id' function to identify the different objects
#       as sometimes a 'getattr' will produce values instead of returning
#       a single one.
# TODO: Fix the problem when clicking on the module name
# TODO: Allow to close containers
# TODO: Allow to choose between alpha and source-code order for methods
# TODO: Add filter / search
# TODO: Add parents in the class
# TODO: Add 'related' (same constants, same type, etc) in the same scope
# TODO: Related like 'Storage' and 'SQLStorage', or 'ModelError',
#       'InventoryError'
# TOOD: Add 'important' tags for classes that have many methods
# TODO: Add Exceptions group

import os, sys, types, string, fnmatch, re, pprint, functools
import smalldoc
from   .model      import Documenter
from   .drivers.sg import SugarDriver

try:
	import reporter
	logging = reporter.bind("smalldoc", template=reporter.TEMPLATE_COMMAND)
except ImportError as e:
	import logging

__version__ = "0.6.0"
__doc__ = """\
Smalldoc is a tool to generate a one-page interactive API documentation for the
listed Python modules.
"""

RE_PATH_SUFFIX = re.compile("@(\w+)$")

# ------------------------------------------------------------------------------
#
# MAIN
#
# ------------------------------------------------------------------------------


DESCRIPTION = """\
Smalldoc is an language-agnostic API documentation generator that produce interactive,
JavaScript-based documentation that have a SmallTalk feel.

See <http://www.github.com/sebastien/smalldoc> for more information."""
USAGE = "%prog [options] module.py module.name ... [output file]"

# A mapping of file extensions (without the dot) and driver names
# to the canonical driver name
DRIVERS_EXT = {
	"py"     : "python",
	"sg"     : "sugar",
	"sjs"    : "sugar",
	"spy"    : "sugar",
	"txto"   : "texto",
	"js"     : "output",
	"json"   : "output",
	"html"   : "output",
	# ".md"   : "md",
	# ".rst"  : "rst",
}

# The mapping between
DRIVERS = {
	"python" : "smalldoc.drivers.py.PythonDriver",
	"sugar"  : "smalldoc.drivers.sg.SugarDriver",
	"texto"  : "smalldoc.drivers.txto.TextoDriver",
}

def run( args, stdout=sys.stdout, interactive=True ):
	"""Runs `smalldoc` as a command line tool"""
	if type(args) not in (type([]), type(())): args = [args]
	from optparse import OptionParser
	# We create the parse and register the options
	oparser = OptionParser(prog="smalldoc", description=DESCRIPTION,
	usage=USAGE, version="Smalldoc " + __version__)
	oparser.add_option("-o", "--output", action="append", dest="output", default=[],
		help="Outputs the documentation to the given file (format will be detected based on extension)")
	oparser.add_option("-f", "--format", dest="format", default="html", choices=("json", "html", "js"),
		help="Specifies the output format, used when format cannot be guessed from output.")
	oparser.add_option("-L", "--library", action="append", dest="path",
		help="Adds the given path as a source of modules/libraries")
	oparser.add_option("-t", "--title", dest="title",
		help="Title for the generated documentation")
	# We parse the options and arguments
	options, args = oparser.parse_args(args=args)
	# We modify the sys.path
	if options.path:
		options.path.reverse()
		for arg in options.path:
			sys.path.insert(0, arg)
	documenter = Documenter()
	# The lazy map of drivers, create as they're needed
	drivers    = {}
	def get_driver( name, drivers=drivers ):
		"""Lazily creates the drivers with the given name."""
		if name not in drivers:
			symbol_name = DRIVERS[name]
			module_name, class_name = symbol_name.rsplit(".", 1)
			# Python __import__ does not return the imported symbol but its
			# root module, so we need to traverse it.
			path          = symbol_name.split(".")
			driver_class  = functools.reduce(lambda a,b:getattr(a, b), path[1:], __import__(module_name))
			driver        = driver_class(documenter, options.path, logger=logging)
			drivers[name] = driver
		return drivers[name]
	# And now document the module
	for arg in args:
		driver = DRIVERS_EXT.get(os.path.splitext(arg)[1][1:])
		# If the path does not exist and is like PATH@DRIVER
		# we extract the driver and force it
		if not os.path.exists(arg) and "@" in arg:
			i      = arg.find("@")
			suffix = RE_PATH_SUFFIX.match(arg[i:])
			if suffix:
				driver = suffix.group(1)
				driver = DRIVERS_EXT.get(driver) or driver
				arg = arg[:i]
		# We infer the driver from the file extension
		if driver == "output":
			options.output.append(arg)
		elif driver in DRIVERS:
			get_driver(driver).parse(arg)
		elif driver:
			logging.error("Driver not found: `{0}`".format(driver))
		else:
			logging.error("No driver defined for: `{0}`".format(arg))
	if args:
		# And finally, we write the output
		title = options.title or "API"
		for o in options.output or ("-"):
			ext = os.path.splitext(o)[1][1:]
			f = ext if ext in ("html", "json", "js") else options.format
			if o == "-":
				o = stdout
				documenter.write(o, f)
			else:
				with open(o, "w") as s:
					documenter.write(s, f)
	elif interactive:
		# If there was no argument, we print the help
		oparser.print_help()
	return documenter

if __name__ == "__main__":
	run(sys.argv[1:])

# EOF
