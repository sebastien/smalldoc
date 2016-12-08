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

import os, sys, types, string, fnmatch, re, pprint
import smalldoc

# Kiwi support allows to expand the markup within Smalldoc
try:
	import texto, texto.main, texto.parser
except ImportError:
	texto = None

# LambdaFactory allows to generate Smalldoc documentation from any program model
try:
	import lambdafactory.interfaces
except ImportError:
	lambdafactory = None

__version__ = "0.5.9"
__doc__ = """\
Smalldoc is a tool to generate a one-page interactive API documentation for the
listed Python modules.
"""

# ------------------------------------------------------------------------------
#
# UTILITIES
#
# ------------------------------------------------------------------------------

KEY_MODULE          = "Modules"
KEY_CLASS           = "Classes"
KEY_FUNCTION        = "Functions"
KEY_METHOD          = "Methods"
KEY_CONSTRUCTOR     = "Constructor"
KEY_CLASS_METHOD    = "Class Methods"
KEY_CLASS_ATTRIBUTE = "Class Attribute"
KEY_ATTRIBUTE       = "Attributes"
KEY_VALUE           = "Values"
KEY_PARENT          = "Bases"
MOD_INHERITED       = "Inherited"

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

# Special attributes are keys that are represented differently. The key is the
# name of the attributes within the Python object, the value is the displayed
# name (as a string), or a function that will transform the value into a string
# that will be displayed (as the __bases__ illustrates it)
def format_classParents(parents):
	if not parents:
		return "<i>Base class</i>"
	else:
		return ", ".join(map(lambda c:c.__name__, parents))

SPECIAL_ATTRIBUTES = {
	"__init__":"constructor",
	"__cmp__":"compare to",
	"__eq__":"equals",
	"__del__":"delete",
	"__getitem__":"get item",
	"__setitem__":"set item",
	"__len__":"length",
	"__iter__":"iterator",
	"__call__":"when invoked",
	"__str__":"string conversion",
	"__repr__":"string repr",
	"__bases__":format_classParents
}

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
		self._markup            = None
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

	def _isExternalValue( self, value, parent=None ):
		"""Tells if the given value is defined in an external module or not."""
		# TypeType children are assumed to be always internal
		if parent and type(parent) == types.TypeType:
			return False
		if hasattr(value, "__module__") and \
		not getattr(value, "__module__") == self._currentModule.__name__:
			# TODO: We should tell that this module imports another one,
			# which is the __module__ value
			return True
		return False

	def _keysByTypeHelper( self, keysbytype, value ):
		"""This function may be called to enrich the keysByType result with
		additional keys and values.

		This hook was added specifically for Python dir() method not listing the
		`__bases__` attribute of class objects, which is necessary."""
		# If the something is a class, we add class-specific attributes which
		# are not detected by "dir()" by default
		if type(value) == types.ClassType:
			keysbytype.setdefault(KEY_PARENT, []).append("__bases__")

	def _keysByType( self, something ):
		"""Returns a dictionnary containing the keys of the given object dictionnary
		grouped by type and sorted alphabetically."""
		result = {}
		# We dispatch the values by type in the result dictionnary
		for key in self._getAllSlotsNames(something):
			# We see if the key is inherited or not
			if key not in self._getOwnSlotsNames(something): mod = MOD_INHERITED
			else: mod = ""
			value  = self._getAttribute(something, key)
			# FIXME: Abstract this
			# We check if the value should be taken into account, that is we
			# ensure that the function or class belongs to the current module.
			if self._isExternalValue(value, something):
				continue
			values = result.setdefault(mod + self.typeToName(value), [])
			values.append(key)
		# We invoke the _keysByTypeHelper before going further
		self._keysByTypeHelper(result, something)
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
		t = self.typeToName(something)
		if t == KEY_CLASS: return True
		if t != KEY_MODULE: return False
		name = self._getName(something)
		for pattern in self._acceptedModules:
			if fnmatch.fnmatch(name, pattern):
				return True
		return False

	def isSkipped( self, name, value ):
		"""Tells wether the given name or value will be skipped. Basically,
		some names (like __builtins__, etc) as well as unaccepted modules will
		be skipped."""
		if name.startswith("__") and name not in (SPECIAL_ATTRIBUTES.keys()): return True
		if type(value) in (types.ClassType, types.ModuleType) \
		and not self.recurses(value):
			return True
		return False

	def representation( self, something ):
		"""Gives the Python-representation of the given object."""
		if type(something) in (types.FunctionType, types.MethodType,
		types.UnboundMethodType):
			return self._describeFunction(something)
		if type(something) in (tuple, list, dict, unicode, str):
			return self._formatLiteral(something)
		else:
			return self._formatLiteral(something)

	def describe( self, something, name ):
		"""Gets a description for the given object. This looks for a __doc__
		attribute in the object, otherwise returns its type and representation.
		This returns a div with a title and paragraph.This is a rather long
		text."""
		# FIXME
		# return self._formatObject(something)
		this_id = "d_" + self.id(something)
		if self._contents.get(this_id) != None: return self._contents.get(this_id)
		result = "<div id='%s' class='description'>" % (this_id)
		result += "<h1>%s</h1>" % (self.describeType(something, name))
		result += "<div class='representation'>"
		result += self.representation(something)
		result += "</div>"
		result += "<div class='docstring'>"
		if self._hasDocumentation(something):
			if self._markup == "texto" and texto:
				# We correct the first line indentation of the text if necessary
				docstring = self._getDocumentation(something)
				first_line_indent = texto.parser.Parser.getIndentation(docstring[:docstring.find("\n")])
				text_indent = texto.parser.Parser.getIndentation(docstring)
				docstring = " " * (text_indent - first_line_indent)  + docstring
				r = texto.main.text2htmlbody(docstring.decode("utf8"))
				result += r
			else:
				result += "<div class='raw'>%s</div>".replace("\n", "<br />") % (html_escape(self._getDocumentation(something)))
		else:
			result += "<span class='undocumented'>Undocumented</span>"
		about = "<div class='about'>generated by <a href='http://github.com/sebastien/smalldoc' target=smalldoc>smalldoc</a></div>"
		result += "</div>" + about + "</div>"
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
		self._descriptions.append(self.describe(something, name))
		self._path.pop()
		self._visited[this_id] = True
		return result

	def documentModule( self, name ):
		"""This is the main function you should call to document a module. You
		simply have to give the module name, and that's all."""
		module = None
		# FIXME: Abstract this (like _resolveModule)
		try:
			exec "import %s as module" % (name)
			log("Documenting '%s'" % (name))
		except Exception, e:
			self._error("Cannot import module '%s'\n%s" % (name,e))
			return
		assert module
		self._currentModule = module
		self._modules.append(module)
		self._formatModule (name, module)
		self.document(name, module, 0)

	def list( self, name, something, level=0 ):
		"""Returns a layer containing the list of fields in this object. This
		implies that this object can be "dir'ed", and returns True when given to
		the 'Documenter.recurse' method."""
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
					try:
						is_documented = self._getDocumentation(child)
					except:
						is_documented = False
					link = "href='javascript:documentElement(\"%s\",\"%s\");'" % (this_id, child_id)
					type_name = self.typeToName(child)
					prefix = "&sdot;"
					if type_name in (KEY_CLASS_METHOD, KEY_METHOD): prefix = "&fnof;"
					if type_name == KEY_FUNCTION: prefix = "&lambda;"
					if type_name == KEY_CLASS: prefix = "&Tau;"
					if attribute.upper() == attribute: prefix = "&bull;"
					if attribute in SPECIAL_ATTRIBUTES:
						# Special attribute values are either strings or
						# functions that convert the child value to a string
						# (which is the case for __bases__, for instance)
						label = SPECIAL_ATTRIBUTES[attribute]
						if type(label) not in (str, unicode):
							label = label(child)
							if label == None: continue
						prefix = "&equiv;"
						attribute =  "<span class='special %s'>%s</span>" % (attribute, label)
					elif attribute.startswith("__"):
						attribute =  "<span class='private'>%s</span>" % ( attribute)
					elif attribute.startswith("_"):
						attribute =  "<span class='protected'>%s</span>" % ( attribute)
					result += """<div class='slot %s'><span
					class='prefix'>%s</span><a %s>%s</a></div>""" % (is_documented and "documented" or "undocumented", prefix, link, attribute)
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

	def _hasDocumentation( self, something ):
		return hasattr(something, "__doc__") and something.__doc__

	def _getDocumentation( self, something ):
		return getattr(something, "__doc__")

	def _getAttribute( self, o, name ):
		return getattr(o, name)

	def _getName( self, something ):
		return something.__name__

	def _getOwnSlotsNames( self, something ):
		return something.__dict__

	def _getAllSlotsNames( self, something ):
		return dir(something)

	def _describeFunction( self, function ):
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

	def typeToName( self, a_value ):
		"""Normalizes the given type to a name. Basically, this will return either
		'Module', 'Class', 'Function' or 'Value'."""
		a_type = type(a_value)
		if a_type == types.ModuleType: return KEY_MODULE
		elif a_type == types.ClassType: return KEY_CLASS
		elif a_type == types.TypeType: return KEY_CLASS
		elif a_type  == types.FunctionType: return KEY_FUNCTION
		elif a_type in (types.MethodType, types.UnboundMethodType): return KEY_METHOD
		elif repr(a_value).startswith("<class '"): return KEY_CLASS
		else: return KEY_VALUE

	def describeType( self, value, slotName ):
		"""Gives a detailed, human-readable string describing the given type."""
		a_type = self.typeToName(value)
		name = lambda o,c="",suffix="":"<span class='name%s'>%s%s</span>" % (" " + c if c else "", o if isinstance(o, str) else o.__name__,suffix)
		if a_type == KEY_MODULE:
			return "Module " + name(value)
		if a_type == KEY_CLASS:
			return "Class " + name(value)
		if a_type == KEY_FUNCTION:
			return "Function " + name(value)
		if a_type == KEY_METHOD:
			return "Method " + name(value.im_class, "parent", suffix=".") + name(value)
		if a_type == KEY_PARENT:
			return "Parent " + name(value)
		else:
			return type(value).__name__ + " " + name(slotName)

	def toHTML( self, title ):
		with  open(os.path.dirname(os.path.abspath(smalldoc.__file__)) + "/smalldoc.tmpl", "rt") as template_f:
			template   = string.Template(template_f.read())
		# We fill the template
		if not self._modules: return ""
		if self._modulesNavigation:
			modules_nav = self._modulesNavigation + "</ul></div>"
		else:
			modules_nav = ""
		return template.substitute(
			MAIN         = self.id(self._modules[0]),
			MODULES      = string.Template(modules_nav).substitute(TITLE=title),
			CONTENT      = "".join(self._contents.values()),
			DESCRIPTIONS = "".join(self._descriptions),
			TITLE        = title
		)

	# =========================================================================

	def _formatLiteral( self, value ):
		return "<code>%s</code>" % (html_escape(pprint.pformat(value)))

	def _formatModule( self, name, module ):
		if not self._modulesNavigation:
			self._modulesNavigation  = "<div class='container'><div class='name'>$TITLE</div>"
			self._modulesNavigation += "<div class='title'>Modules</div>"
			self._modulesNavigation += "<ul class='group'>"
		self._modulesNavigation += \
		  "<li><span class='prefix'>M</span><a href='javascript:documentElement(\"%s\");'>%s</a><li>" \
		  % (self.id(module), name)

	def _formatDocumentation( self, docstring ):
		"""Formats the given docstring"""
		if self._markup == "texto" and texto and texto.main:
			# We correct the first line indentation of the text if necessary
			first_line_indent = texto.core.Parser.getIndentation(docstring[:docstring.find("\n")])
			text_indent = texto.core.Parser.getIndentation(docstring)
			docstring = " " * (text_indent - first_line_indent)  + docstring
			r = texto.main.text2htmlbody(docstring.decode("utf8"))
			result += r
		else:
			result += "<div class='raw'>%s</div>".replace("\n", "<br />") % (html_escape(self._getDocumentation(something)))

	def _formatObject( self, something ):
		this_id = "d_" + self.id(something)
		if self._contents.get(this_id) != None: return self._contents.get(this_id)
		result = "<div id='%s' class='description'>" % (this_id)
		result += "<h1>%s</h1>" % (self.describeType(something))
		result += "<div class='representation'>"
		result += self.representation(something)
		result += "</div>"
		result += "<div class='docstring'>"
		if description["documentation"]:
			result += description["documentation"]
		else:
			result += "<span class='undocumented'>Undocumented</span>"
		result += "</div></div>"
		self._contents[this_id] = result
		return result

# ------------------------------------------------------------------------------
#
# LAMBDA FACTORY DOCUMENTER
#
# ------------------------------------------------------------------------------

class LambdaFactoryDocumenter(Documenter):
	"""This is the class that is responsible for producing the documentation for
	the given lambda-factory based objects.

	See <http://www.github.com/sebastien/lambdafactory> for more details on that."""

	def __init__( self, modules=None, encoding='utf-8' ):
		Documenter.__init__(self, modules, encoding)
		self._markup = "texto"
		if not lambdafactory:
			raise ImportError("Lambda factory is required: <http://www.ivy.fr/lambdafactory>")

	def documentModule( self, module, name=None ):
		"""This is the main function you should call to document a module. You
		simply have to give the module name, and that's all."""
		assert isinstance(module, lambdafactory.interfaces.IModule)
		self._currentModule = module
		self._modules.append(module)
		self.document(name or module.getName(), module, 0)
		if not self._modulesNavigation:
			self._modulesNavigation  = "<div class='container'><div class='name'>$TITLE</div>"
			self._modulesNavigation += "<div class='title'>Modules</div>"
			self._modulesNavigation += "<ul class='group'>"
		self._modulesNavigation += \
		  "<li><span class='prefix'>M</span><a href='javascript:documentElement(\"%s\");'>%s</a><li>" \
		  % (self.id(module), name or module.getName())

	def _hasDocumentation( self, something ):
		return something.getDocumentation()

	def _getDocumentation( self, something ):
		return something.getDocumentation().getContent()

	def _getAttribute( self, o, name ):
		return o.getSlot(name)

	def _getName( self, something ):
		return something.getName()

	def _getOwnSlotsNames( self, something ):
		return [name for name,_ in something.getSlots()]

	def _getAllSlotsNames( self, something ):
		# FIXME: Bad, bad, bad !
		return [name for name,_ in something.getSlots()]

	def _describeFunction( self, function ):
		"""Utility function that returns an HTML representation of the function
		prototype."""
		name = function.getAbsoluteName().replace(".", " ").split()
		prefix = name[:-1]
		suffix = name[-1]
		name = "<span class='module-prefix'>%s</span> <span class='name'>%s</span>" % (".".join(prefix), suffix)
		args = []
		for arg in function.getArguments():
			a = arg.getName()
			if arg.getTypeDescription(): a += ":" + arg.getTypeDescription()
			# FIXME: Should translate the value back to Sugar
			if arg.isOptional(): a+="="+str(arg.getDefaultValue())
			if arg.isRest(): a+="..."
			if arg.isKeywordsRest(): a+="=..."
			args.append(a)
		return "<code>%s (<span class='function-arguments'>%s</span> )</code>" % (name,  ", ".join(args))

	def _isExternalValue( self, value, parent=None ):
		"""Tells if the given value is defined in an external module or not."""
		return False

	def _keysByTypeHelper( self, keysbytype, value ):
		"""Nothing to be done here."""
		return

	def representation( self, something ):
		"""Gives the Sugar-representation of the given object."""
		lif = lambdafactory.interfaces
		if isinstance(something, lif.IFunction):
			return self._describeFunction(something)
		if type(something) in (tuple, list, dict, unicode, str):
			return "<code>%s</code>" % (html_escape(repr(something)))
		else:
			return ""

	def typeToName( self, a_value ):
		"""Normalizes the given type to a name. Basically, this will return either
		'Module', 'Class', 'Function' or 'Value'."""
		lif = lambdafactory.interfaces
		if   isinstance(a_value, lif.IModule): return KEY_MODULE
		elif isinstance(a_value, lif.IClass): return KEY_CLASS
		elif isinstance(a_value, lif.IConstructor): return KEY_CONSTRUCTOR
		elif isinstance(a_value, lif.IClassMethod): return KEY_CLASS_METHOD
		elif isinstance(a_value, lif.IMethod): return KEY_METHOD
		elif isinstance(a_value, lif.IFunction): return KEY_FUNCTION
		elif isinstance(a_value, lif.IClassAttribute): return KEY_CLASS_ATTRIBUTE
		elif isinstance(a_value, lif.IAttribute): return KEY_ATTRIBUTE
		else: return KEY_VALUE

	def describeType( self, value ):
		"""Gives a detailed, human-readable string describing the given type."""
		a_type = self.typeToName(value)
		name = lambda o:"<span class='name'>%s</span>" % (o)
		if a_type == KEY_MODULE:
			return "Module " + name(value.getName())
		if a_type == KEY_CLASS:
			return "Class " + name(value.getName())
		if a_type == KEY_FUNCTION:
			return "Function " + name(value.getName())
		if a_type == KEY_METHOD:
			return "Method " + name(value.getName())
		if a_type == KEY_PARENT:
			# TODO
			return "Parent " + name(value)
		else:
			return value.__class__.__name__

# ------------------------------------------------------------------------------
#
# MAIN
#
# ------------------------------------------------------------------------------

OPT_PYTHONPATH = "Extends the PYTHONPATH with the given path"
OPT_ACCEPTS    = "Glob that matches modules names that will also be documented"
OPT_COMPACT    = "Outputs a compact HTML (slower)"
OPT_MARKUP     = "Uses the given markup ('none', 'rst' or 'texto') to process docstrings"
OPT_BODY       = "Only outputs the HTML document body."""
OPT_TITLE      = "Specifies the title to be used in the resulting HTML"
OPT_ENCODING   = "Specifies the encoding of the strings found in the given modules"
DESCRIPTION    = """\
Smalldoc is a Python API documentation generator that produce interactive,
JavaScript-based documentation that have a SmallTalk feel. It is inspired from
the Io Language API reference <http://www.iolanguage.com/docs/reference/>.

See <http://www.github.com/sebastien/smalldoc> for more information."""
USAGE          = "%prog [options] module.py module.name ... [output file]"

def run( args ):
	"""Runs Smalldoc as a command line tool"""
	if type(args) not in (type([]), type(())): args = [args]
	from optparse import OptionParser
	# We create the parse and register the options
	oparser = OptionParser(prog="smalldoc", description=DESCRIPTION,
	usage=USAGE, version="Smalldoc " + __version__)
	oparser.add_option("-p", "--path", action="append", dest="pythonpath",
		help=OPT_PYTHONPATH)
	oparser.add_option("-a", "--accepts", action="append", dest="accepts",
		help=OPT_ACCEPTS)
	oparser.add_option("-c", "--compact", action="store_true", dest="compact",
		help=OPT_COMPACT)
	oparser.add_option("-m", "--markup", action="store", dest="markup",
		help=OPT_MARKUP, default="rst")
	oparser.add_option("-b", "--body", action="store_true", dest="body",
		help=OPT_BODY)
	oparser.add_option("-t", "--title", dest="title",
		help=OPT_TITLE)
	oparser.add_option("-e", "--encoding", dest="encoding", default="utf-8",
		help=OPT_ENCODING)
	# We parse the options and arguments
	options, args = oparser.parse_args(args=args)
	documenter = Documenter(options.accepts, encoding=options.encoding)
	documenter._markup = options.markup
	lf_documenter = None
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
		elif arg.endswith(".sjs"):
			dir_path = os.path.abspath(os.path.dirname(arg))
			if dir_path not in sys.path: sys.path.append(dir_path)
			arg = os.path.basename(arg)
			arg = os.path.splitext(arg)[0]
			documenter = LambdaFactoryDocumenter() if not isinstance(documenter, LambdaFactoryDocumenter) else documenter
			import sugar.main
			program    = sugar.main.parseFile(arg)
			#documenter.documentModule(arg)
		elif arg.lower().endswith(".html"):
			target_html = arg
		else:
			documenter.documentModule(arg)
	# We eventually return the HTML file
	if args:
		title = options.title or "Python API documentation (Smalldoc)"
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
