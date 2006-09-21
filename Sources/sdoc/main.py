#!/usr/bin/env python
# Encoding: iso-8859-1
# vim: tw=80 ts=4 sw=4 noet
# -----------------------------------------------------------------------------
# Project   : SDoc - Python Documentation introspection
# -----------------------------------------------------------------------------
# Author    : Sebastien Pierre                               <sebastien@ivy.fr>
# License   : Revised BSD License
# -----------------------------------------------------------------------------
# Creation  : 30-Mar-2006
# Last mod  : 21-Sep-2006
# -----------------------------------------------------------------------------

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

import os, sys, types, string, fnmatch, re

try:
	import kiwi.main 
	import kiwi.core
	import StringIO
except ImportError:
	kiwi = None

__version__ = "0.4.3"
__doc__ = """\
SDOc is a tool to generate a one-page interactive API documentation for the
listed Python modules."""

# ------------------------------------------------------------------------------
#
# UTILITIES
#
# ------------------------------------------------------------------------------

KEY_MODULE    = "Modules"
KEY_CLASS     = "Classes"
KEY_FUNCTION  = "Functions"
KEY_METHOD    = "Methods"
KEY_VALUE     = "Values"
MOD_INHERITED = "Inherited"
KEYS_ORDER    = (KEY_MODULE, KEY_CLASS, KEY_METHOD, KEY_FUNCTION, KEY_VALUE)

COMPACT = {
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
RE_SPACES = re.compile("\s*\n\s*\n+")
def html_escape( text ):
	return RE_SPACES.sub("<br />", str(text).replace("<", "&lt;").replace(">",
	"&gt;"))

def compact_html( text ):
	# Step 1: Splits the text
	SNIP = "<!-- snip-snip-snip-snip-snip-snip -->"
	head, css, script, body = text.split(SNIP)
	# Step 2: We replace the JavaScript
	script = script.replace("documentElement","dO").replace("describeElement","dS")
	body   = body.replace("javascript:documentElement", "javascript:dO").replace("javascript:describeElement","javascript:dS")
	# Step 3: Replaces the CSS
	for complete, compact in COMPACT.items():
		css  = css.replace("." + complete, "." + compact)
		body = body.replace("class='%s'" % (complete), "class='%s'" % (compact))
	return head + css + script + body

def snip_html( html ):
	"""Returns a tuple (CSS_MAIN, CSS_CLASSES, JAVASCRIPT, MODULES,
	DESCRIPTIONS, CONTENT) contains the CSS general definitions, the
	CSS specific classes definition, the JavaScript source code, the content
	of the #modules div, the content of the #descriptions div, the content
	of the #hiddent div. CSS and JavaScript are not enclosed in HTML tags.

	You will have to rebuild your document afterwards. And be sure to define
	#descriptions, #modules, #api and #hidden divs."""
	css_main     = html.split("/* css-main-snip */")[1]
	css_classes  = html.split("/* css-classes-snip */")[1]
	javascript   = html.split("// javascript-snip")[1]
	modules      = html.split("<!-- modules-snip -->")[1]
	descriptions = html.split("<!-- descriptions-snip -->")[1]
	content      = html.split("<!-- hidden-snip -->")[1]
	return css_main, css_classes, javascript, modules, descriptions, content

def typeToName( a_value ):
	"""Normalizes the given type to a name. Basically, this will return either
	'Module', 'Class', 'Function' or 'Value'."""
	a_type = type(a_value)
	if a_type == types.ModuleType: return KEY_MODULE
	elif a_type == types.ClassType: return KEY_CLASS
	elif a_type  == types.FunctionType: return KEY_FUNCTION
	elif a_type in (types.MethodType, types.UnboundMethodType): return KEY_METHOD
	elif repr(a_value).startswith("<class '"): return KEY_CLASS
	else: return KEY_VALUE

def _describeFunction( function ):
	"""Utility function that returns an HTML representation of the function
	prototype."""
	if hasattr(function, "im_func"): function = function.im_func
	try:
		defaults = function.func_defaults
		code     = function.func_code
	except:
		return ""
	args = list(code.co_varnames[:code.co_argcount])
	# We split the args in args / default_args
	if defaults:
		default_args = args[-len(defaults):]
		args         = args[:-len(defaults)]
	else:
		default_args = []
	# We add the default arguments (properly formatted) to the arguments
	# list
	for i in range(len(default_args)):
		d = default_args[i]
		args.append("%s=%s" % (d, repr(defaults[i])) )
	# We append the arguments
	if code.co_flags & 0x0004: # CO_VARARGS
		args.append('*'+code.co_varnames[len(args)])
	if code.co_flags & 0x0008: # CO_VARKEYWORDS
		args.append('**'+code.co_varnames[len(args)])
	return "<code>%s( %s )</code>" % (function.__name__, ", ".join(map(str,args)))

def describeType( value ):
	"""Gives a detailed, human-readable string describing the given type."""
	a_type = typeToName(value)
	name = lambda o:"<span class='name'>%s</span>" % (o.__name__)
	if a_type == KEY_MODULE:
		return "Module " + name(value)
	if a_type == KEY_CLASS:
		return "Class " + name(value)
	if a_type == KEY_FUNCTION:
		return "Function " + name(value)
	if a_type == KEY_METHOD:
		return "Method " + name(value)
	else:
		return type(value).__name__

def log(*args):
	sys.stderr.write("%s\n" % (" ".join(map(str, args))))

def err(*args):
	sys.stderr.write("ERROR: %s\n" % (" ".join(map(str, args))))

# ------------------------------------------------------------------------------
#
# DOCUMENTER
#
# ------------------------------------------------------------------------------

IDS    = {}
RETAIN = []

class Documenter:
	"""This is the class that is responsible for producing the documentation for
	the given objects. It can be later interrogated to create the HTML file that
	will be the documentation."""

	def __init__( self, modules=None, encoding='utf-8' ):
		self._visited           = {}
		self._descriptions      = []
		self._contents          = {}
		self._acceptedModules   = []
		self._currentModule     = None
		self._modules           = []
		self._modulesNavigation = ""
		self._path              = []
		self._errors            = []
		self._encoding          = encoding
		if type(modules) in (str, unicode): self._acceptedModules.append(modules)
		elif modules: self._acceptedModules.extend(modules)

	def _error( self, message ):
		"""Logs an error in this documenter."""
		self._errors.append(message)
		err(message)

	def _sortAlphabetically( self, a, b ):
		"""Predicate that sorts the given strings so that uppercase are first,
		then mixed case, then lowercase"""
		def f(a):
			if   a.upper() == a.upper(): a = (2, a)
			elif a[0].upper() == a[0].upper(): a =  (1, a)
			else: a = (0, a)
			return a
		return cmp(f(a), f(b))

	def _keysByType( self, something ):
		"""Returns a dictionnary containing the keys of the given object dictionnary
		grouped by type and sorted alphabetically."""
		result = {}
		# We dispatch the values by type in the result dictionnary
		for key in dir(something):
			# We see if the key is inherited or not
			if key not in something.__dict__.keys(): mod = MOD_INHERITED
			else: mod = ""
			value  = self._getAttribute(something, key)
			# We check if the value should be taken into account, that is we
			# ensure that the function or class belongs to the current module.
			if hasattr(value, "__module__") and \
			not getattr(value, "__module__") == self._currentModule.__name__:
				# TODO: We should tell that this module imports another one,
				# which is the __module__ value
				continue
			values = result.setdefault(mod + typeToName(value), [])
			values.append(key)
		# Then, for a particular type, we sort the items
		for key, values in result.items():
			values.sort(self._sortAlphabetically)
		return result

	def id( self, something ):
		"""Returns the identifier for this object, as a string."""
		global IDS, RETAIN
		the_id = str(id(something))
		result = IDS.get(the_id)
		if result == None:
			RETAIN.append(something)
			val    = len(IDS)
			limit  = len(string.letters)
			if val < 0:
				result += "0" ; val = abs(val)
			result = ""
			# Converts the given identifier to
			while True:
				mod = val % limit
				val = val / limit
				result += string.letters[mod]
				if val == 0: break
			IDS[the_id] = result
		assert len(RETAIN) == len(IDS.keys()), "%s != %s" % (len(RETAIN), len(IDS.keys()))
		return result

	def recurses( self, something ):
		"""Tells wether the Documenter should recurse on the given object. If
		the object is a class or an accepted module, this will return True,
		False otherwise."""
		t = typeToName(something)
		if t == KEY_CLASS: return True
		if t != KEY_MODULE: return False
		name = something.__name__
		for pattern in self._acceptedModules:
			if fnmatch.fnmatch(name, pattern):
				return True
		return False
	
	def isSkipped( self, name, value ):
		"""Tells wether the given name or value will be skipped. Basically,
		some names (like __builtins__, etc) as well as unaccepted modules will
		be skipped."""
		if name.startswith("__"): return True
		if type(value) in (types.ClassType, types.ModuleType) \
		and not self.recurses(value):
			return True
		return False

	def representation( self, something ):
		"""Gives the Python-representation of the given object."""
		if type(something) in (types.FunctionType, types.MethodType,
		types.UnboundMethodType):
			return _describeFunction(something)
		if type(something) in (tuple, list, dict, unicode, str):
			return "<code>%s</code>" % (html_escape(repr(something)))
		else:
			return ""

	def describe( self, something ):
		"""Gets a description for the given object. This looks for a __doc__
		attribute in the object, otherwise returns its type and representation.
		This returns a div with a title and paragraph.This is a rather long
		text."""
		this_id = "d_" + self.id(something)
		if self._contents.get(this_id) != None: return self._contents.get(this_id)
		result = "<div id='%s' class='description'>" % (this_id)
		result += "<h1>%s</h1>" % (describeType(something))
		result += "<div class='representation'>"
		result += self.representation(something)
		result += "</div>"
		result += "<div class='docstring'>"
		if hasattr(something, "__doc__") and something.__doc__:
			if kiwi.main:
				# We correct the first line indentation of the text if necessary
				docstring = something.__doc__
				first_line_indent = kiwi.core.Parser.getIndentation(docstring[:docstring.find("\n")])
				text_indent = kiwi.core.Parser.getIndentation(docstring)
				docstring = " " * (text_indent - first_line_indent)  + docstring
				s = StringIO.StringIO(docstring)
				_, r = kiwi.main.run("-m --input-encoding=%s --body-only --" % (self._encoding), s, noOutput=True)
				s.close()
				result += r
			else:
				result += "%s" % (html_escape(something.__doc__))
		else:
			result += "<span class='undocumented'>Undocumented</span>"
		result += "</div></div>"
		self._contents[this_id] = result
		return result

	def document( self, name, something, level=0 ):
		"""Document the given element, which has the given name."""
		this_id = self.id(something)
		if self._visited.get(this_id): return ""
		self._path.append(name)
		result = ""
		if level == 0 or self.recurses(something):
			result += self.list(name, something, level)
		self._descriptions.append(self.describe(something))
		self._path.pop()
		self._visited[this_id] = True
		return result
	
	def documentModule( self, name ):
		"""This is the main function you should call to document a module. You
		simply have to give the module name, and that's all."""
		module = None
		try:
			exec "import %s as module" % (name)
			log("Documenting '%s'" % (name))
		except ImportError, e:
			self._error("Cannot import module '%s'\n%s" % (name,e))
			return
		assert module
		self._currentModule = module
		self._modules.append(module)
		self.document(name, module, 0)
		if self._modulesNavigation: self._modulesNavigation += " &bull; "
		else: self._modulesNavigation = "API : "
		self._modulesNavigation += \
		  "<a href='javascript:documentElement(\"%s\");'>%s</a>" \
		  % (self.id(module), name)

	def list( self, name, something, level=0 ):
		"""Returns a layer containing the list of fields in this object. This
		implies that this object can be "dir'ed", and returns True when given to
		the @Documenter.recurse method."""
		# If the object was alredy visited, we skip it and return an empty
		# string
		this_id = self.id(something)
		if self._visited.get(this_id): return ""
		keys   = self._keysByType(something)
		result = ""
		result += "<div id='%s' class='%s'>" % (this_id, level == 0 and "root" or "container")
		result += "<div class='name'><a href='javascript:describeElement(\"%s\");'>%s</a></div>" % (this_id, name)
		# We list the children names, grouped by type
		has_attributes = False
		for some_type in KEYS_ORDER:
			attributes = keys.get(some_type) 
			inherited  = keys.get(MOD_INHERITED + some_type)
			if not attributes and not inherited: continue
			# We iterate on the groups
			for group in (attributes, inherited):
				if not group: continue
				group_printed  = False
				if group == inherited: mod = "Inhertied "
				else: mod = ""
				# For each attribute of the group
				for attribute in group:
					child = self._getAttribute(something, attribute)
					if self.isSkipped(attribute, child): continue
					# We print the group if it was not already printed. We have to
					# do it here, because some groups may only contain values that
					# will be skipped
					if not group_printed:
						result += "<div class='title'>%s</div class='title'><div class='group'>" % ( mod + some_type )
						group_printed = True
					child_id = self.id(child)
					is_documented = getattr(child, "__doc__") and "documented" or "undocumented"
					link = "href='javascript:documentElement(\"%s\",\"%s\");'" % (this_id, child_id)
					type_name = typeToName(child)
					prefix = "&sdot;"
					if type_name == KEY_METHOD: prefix = "&fnof;"
					if type_name == KEY_FUNCTION: prefix = "&lambda;"
					if type_name == KEY_CLASS: prefix = "&Tau;"
					if attribute.upper() == attribute: prefix = "&bull;"
					result += """<span class='%s'><span class='prefix'>%s</span><a %s>%s</a></span><br />""" % (is_documented, prefix, link, attribute)
					# We document the child attribute
					t = self.document(attribute, child, level + 1)
					if t: self._contents[child_id] = t
					has_attributes = True
				if group_printed: result += "</div>"
		if not has_attributes:
			result += "<span class='noattributes'>No attributes</span>"
		result += "</div>"
		self._contents[this_id] = result
		return result
	
	def _getAttribute( self, o, name ):
		return getattr(o, name)

	def toHTML( self, title ):
		template_f = file(os.path.dirname(os.path.abspath(__file__)) + "/sdoc.tmpl", "rt")
		template   = string.Template(template_f.read())
		template_f.close()
		# We fill the template
		if not self._modules: return ""
		return template.substitute(
			MAIN         = self.id(self._modules[0]),
			MODULES      = self._modulesNavigation,
			CONTENT      = "".join(self._contents.values()),
			DESCRIPTIONS = "".join(self._descriptions),
			TITLE        = title
		)

# ------------------------------------------------------------------------------
#
# MAIN
#
# ------------------------------------------------------------------------------

OPT_PYTHONPATH = "Extends the PYTHONPATH with the given path"
OPT_ACCEPTS    = "Glob that matches modules names that will also be documented"
OPT_COMPACT    = "Outputs a compact HTML (slower)"
OPT_BODY       = "Only outputs the HTML document body."""
OPT_TITLE      = "Specifies the title to be used in the resulting HTML"
OPT_ENCODING   = "Specifies the encoding of the strings found in the given modules"
DESCRIPTION    = """\
SDoc is a Python API documentation generator that produce interactive,
JavaScript-based documentation that have a SmallTalk feel. It is inspired from
the Io Language API reference <http://www.iolanguage.com/docs/reference/>.

See <http://www.ivy.fr/sdoc> for more information."""
USAGE          = "%prog [options] module.py module.name ..."

def run( args ):
	"""Runs SDoc as a command line tool"""
	if type(args) not in (type([]), type(())): args = [args]
	from optparse import OptionParser
	# We create the parse and register the options
	oparser = OptionParser(prog="sdoc", description=DESCRIPTION,
	usage=USAGE, version="SDoc " + __version__)
	oparser.add_option("-p", "--path", action="append", dest="pythonpath",
		help=OPT_PYTHONPATH)
	oparser.add_option("-a", "--accepts", action="append", dest="accepts",
		help=OPT_ACCEPTS)
	oparser.add_option("-c", "--compact", action="store_true", dest="compact",
		help=OPT_COMPACT)
	oparser.add_option("-b", "--body", action="store_true", dest="body",
		help=OPT_BODY)
	oparser.add_option("-t", "--title", dest="title",
		help=OPT_TITLE)
	oparser.add_option("-e", "--encoding", dest="encoding", default="utf-8",
		help=OPT_ENCODING)
	# We parse the options and arguments
	options, args = oparser.parse_args(args=args)
	documenter   = Documenter(options.accepts, encoding=options.encoding)
	# We modify the sys.path
	if options.pythonpath:
		options.pythonpath.reverse()
		for arg in options.pythonpath:
			log("Adding path '%s'..." % (arg))
			sys.path.insert(0, arg)
	# And now document the module
	target_html = None
	for arg in args:
		if arg.endswith(".py"):
			dir_path = os.path.abspath(os.path.dirname(arg)) 
			if dir_path not in sys.path: sys.path.append(dir_path)
			arg = os.path.basename(arg)
			arg = os.path.splitext(arg)[0]
			documenter.documentModule(arg)
		elif arg.lower().endswith(".html"):
			target_html = arg
		else:
			documenter.documentModule(arg)
	# We eventually return the HTML file
	if args:
		title = options.title or "Python API documentation (SDoc)"
		html = documenter.toHTML(title=title)
		if options.compact: html = compact_html(html)
	else:
		html = ""
		oparser.print_help()
	if options.body:
		html = html.split("<!-- body -->")[1]
	# And optionnaly save the html
	if target_html:
		open(target_html, "w").write(html)
		html = "HTML documentation generated: " + target_html
	return html

if __name__ == "__main__":
	print run(sys.argv[1:])

# EOF
