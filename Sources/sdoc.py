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
# Last mod  : 31-Mar-2006
# History   :
#             31-Mar-2006 - Added inheritance support, added multiple modules
#             30-Mar-2006 - First implementation
# -----------------------------------------------------------------------------

# TODO: Optimize by using a StringIO instead of concateating strings
# TODO: Add a way to generate shorter HTML (1 char class names, shorter id and
# js functions)

import os, sys, types, string, fnmatch

# ------------------------------------------------------------------------------
#
# UTILITIES
#
# ------------------------------------------------------------------------------

KEY_MODULE    = "Modules"
KEY_CLASS     = "Classes"
KEY_FUNCTION  = "Functions"
KEY_VALUE     = "Values"
MOD_INHERITED = "Inherited"
KEYS_ORDER    = (KEY_MODULE, KEY_CLASS, KEY_FUNCTION, KEY_VALUE)

def html_escape( text ):
	return str(text).replace("<", "&lt;").replace(">", "&gt;")

def typeToName( a_type ):
	"""Normalizes the given type to a name. Basically, this will return either
	'Module', 'Class', 'Function' or 'Value'."""
	if a_type == types.ModuleType: return KEY_MODULE
	elif a_type == types.ClassType: return KEY_CLASS
	elif a_type in (types.FunctionType, types.MethodType, types.UnboundMethodType): return KEY_FUNCTION
	else: return KEY_VALUE

def _describeFunction( function ):
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
		args.append("%s=%s" % (d, repr(d)) )
	# We append the arguments
	if code.co_flags & 0x0004: # CO_VARARGS
		args.append('*'+code.co_varnames[len(args)])
	if code.co_flags & 0x0008: # CO_VARKEYWORDS
		args.append('**'+code.co_varnames[len(args)])
	return "<code>%s( %s )</code>" % (function.__name__, ", ".join(map(str,args)))

def describeType( value ):
	"""Gives a detailed, human-readable string describing the given type."""
	a_type = type(value)
	name = lambda o:"<span class='name'>%s</span>" % (o.__name__)
	if a_type == types.ModuleType:
		return "Module " + name(value)
	if a_type == types.ClassType:
		return "Class " + name(value)
	if a_type == types.FunctionType:
		return "Function " + name(value)
	if a_type == types.MethodType:
		return "Method " + name(value)
	if a_type == types.UnboundMethodType:
		return "Method " + name(value)
	else:
		return a_type.__name__

# ------------------------------------------------------------------------------
#
# DOCUMENTER
#
# ------------------------------------------------------------------------------

def log(*args):
	sys.stderr.write("%s\n" % (" ".join(map(str, args))))

class Documenter:
	"""This is the class that is responsible for producing the documentation for
	the given objects. It can be later interrogated to create the HTML file that
	will be the documentation."""

	def __init__( self, modules=None ):
		self._visited           = {}
		self._descriptions      = []
		self._contents          = []
		self._acceptedModules   = []
		self._modules           = []
		self._modulesNavigation = ""
		if type(modules) in (str, unicode): self._acceptedModules.append(modules)
		elif modules: self._acceptedModules.extend(modules)

	def id( self, something ):
		"""Returns the identifier for this object, as a string."""
		return "obj-%s" % ( str(id(something)) )

	def _keysByType( self, something ):
		"""Returns a dictionnary containing the keys of the given object dictionnary
		grouped by type and sorted alphabetically."""
		result = {}
		# We dispatch the values by type in the result dictionnary
		for key in dir(something):
			# We see if the key is inherited or not
			if key not in something.__dict__.keys(): mod = MOD_INHERITED
			else: mod = ""
			value  = getattr(something, key)
			values = result.setdefault(mod + typeToName(type(value)), [])
			values.append(key)
		# Then, for a particular type, we sort the items
		for key, values in result.items():
			values.sort()
		return result

	def recurses( self, something ):
		"""Tells wethere the Documenter should recurse on the given object. If
		the object is a class or an accepted module, this will return True,
		False otherwise."""
		if type(something) == types.ClassType: return True
		if type(something) != types.ModuleType: return False
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
		else:
			return "<code>%s</code>" % (html_escape(repr(something)))

	def describe( self, something ):
		"""Gets a description for the given object. This looks for a __doc__
		attribute in the object, otherwise returns its type and representation.
		This returns a div with a title and paragraph.This is a rather long
		text."""
		this_id = self.id(something)
		result = "<div id='desc_%s' class='description'>" % (this_id)
		result += "<h1>%s</h1>" % (describeType(something))
		result += "<div class='representation'>"
		result += self.representation(something)
		result += "</div>"
		result += "<div class='docstring'>"
		if hasattr(something, "__doc__") and something.__doc__:
			result += "%s" % (html_escape(something.__doc__))
		else:
			result += "<span class='undocumented'>Undocumented</span>"
		result += "</div></div>"
		return result

	def document( self, name, something, level=0 ):
		"""Document the given element, which has the given name."""
		this_id = self.id(something)
		if self._visited.get(this_id): return ""
		result = ""
		if level == 0 or self.recurses(something):
			result += self.list(name, something, level)
		self._descriptions.append(self.describe(something))
		return result
	
	def documentModule( self, name ):
		"""This is the main function you should call to document a module. You
		simply have to give the module name, and that's all."""
		module = None
		# FIXME: Raises ImportErrror
		exec "import %s as module" % (name)
		assert module
		self._modules.append(module)
		self.document(name, module, 0)
		if self._modulesNavigation: self._modulesNavigation += " &bull; "
		else: self._modulesNavigation = "APIs : "
		self._modulesNavigation += \
		  "<a href='javascript:documentElement(\"%s\");'>%s</a>" \
		  % (self.id(module), name)

	def list( self, name, something, level=0 ):
		"""Returns a layer containing the list of fields in this object. This
		implies that this object can be "dir'ed", and returns True when given to
		the @Documnenter.recurse method."""
		# If the object was alredy visited, we skip it and return an empty
		# string
		this_id = self.id(something)
		if self._visited.get(this_id): return ""
		keys   = self._keysByType(something)
		result = ""
		result += "<div id='%s' class='%s'>" % (this_id, level == 0 and "root" or "container")
		result += "<div class='name'><a href='javascript:describeElement(\"%s\");'>%s</a></div>" % (this_id, name)
		# We list the children names, grouped by type
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
					child = getattr(something, attribute)
					if self.isSkipped(attribute, child): continue
					# We print the group if it was not already printed. We have to
					# do it here, because some groups may only contain values that
					# will be skipped
					if not group_printed:
						result += "<div class='title'>%s</div class='title'><div class='group'>" % ( mod + some_type )
						group_printed = True
					child_id = self.id(child)
					if self.recurses(child):
						link = "href='javascript:documentElement(\"%s\",\"%s\");'" % (this_id, child_id)
						is_documented = child.__dict__.get("__doc__") and "documented" or "undocumented"
						result += """<span class="%s"><a %s>%s</a></span><br />""" % (is_documented, link, attribute)
					else:
						link = "href='javascript:documentElement(\"%s\",\"%s\");'" % (this_id, child_id)
						result += """<a %s>%s</a><br />""" % (link, attribute)
			if group_printed: result += "</div>"
		result += "</div>"
		self._contents.append(result)
		# We document the chilren too
		for name in dir(something):
			value = getattr(something, name)
			if self.isSkipped(name, value): continue
			t = self.document(name, value, level + 1)
			if t: self._contents.append(t)
		return result
	
	def toHTML( self ):
		template_f = file(os.path.dirname(os.path.abspath(__file__)) + "/sdoc.tmpl", "rt")
		template   = string.Template(template_f.read())
		template_f.close()
		# We fill the template
		return template.substitute(
			MAIN         = self.id(self._modules[0]),
			MODULES      = self._modulesNavigation,
			CONTENT      = "".join(self._contents),
			DESCRIPTIONS = "".join(self._descriptions)
		)

# ------------------------------------------------------------------------------
#
# MAIN
#
# ------------------------------------------------------------------------------

if __name__ == "__main__":
	documenter = Documenter(tuple(s + "*" for s in sys.argv[1:]))
	modules    = ""
	for module in sys.argv[1:]:
		log("Documenting module " + module)
		documenter.documentModule(module)
	print documenter.toHTML()

# EOF
