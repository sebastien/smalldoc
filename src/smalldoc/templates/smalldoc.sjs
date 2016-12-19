@module smalldoc
| Renders `smalldoc` JSON data into a Smalltalk-like documentation browser. The resulting
| document will ony work on modern browsers.
|
| The `smalldoc` module currently implements a simple flat (non-OOP) API, in order to
| minimize dependencies ― the drawback of this approach is that ther can only
| be one instance per document.

@shared FONTS   = "Fira+Mono|Fira+Sans"
@shared DATA    = None
@shared OPTIONS = {
	containers : 3
	data       : "api.json"
}
@shared STATE   = {
	active  : []
	symbols : {}
}

@shared GROUPS = [
	"parent"
	"module"
	"class"
	"class constructor"
	"class attribute"
	"class method"
	"attribute"
	"method"
	"function"
	"value"
]

@function loadCSS fonts=FONTS
	let node = html link {href:"https://fonts.googleapis.com/css?family=" + fonts,rel:"stylesheet"}
	document head appendChild (node)
	return node
@end

@function load path=OPTIONS data
	fetch (path) then {_ json () then (setup)}
@end

@function setup data=DATA
	DATA = data
	let n = ensureNode ("smalldoc", document body)
	ensureNode ("containers",  n)
	ensureNode ("description", n)
	ensureNode ("hidden",      n)
	ensureNode ("about",       n, {_ innerHTML = "<a href='https://github.com/sebastien/smalldoc'>smalldoc</a>"})
	render (data)
	window addEventListener ("hashchange", onHashChange)
	onHashChange ()
@end

@function ensureNode:Node id:String, parent:Node, callback:Function=Undefined
| Ensures that there's an elment with the given `id`, if not
| creates, feeds it to the given `callback` (optional) and adds it
| to the given `parent`.
	var node = document getElementById (id)
	if not node
		node = html div {id:id}
		if callback
			callback (node)
		end
		parent appendChild (node)
	end
	return node
@end

@function render data
	renderContainer (data, "Smalldoc", "document")
@end

@function show symbol, containers=OPTIONS containers
	_clearContainers ()
	_showContainer "__root__"
	let n = (symbol or "") split "."
	n reduce ({r,e|_showContainer (if r -> r + "." + e | e)}, "")
	# Ensures that there is a least M containers
	let c    = n length
	var node = document getElementById "containers"
	while node childNodes length < containers
		var i = (containers - node childNodes length)
		node appendChild (ensureNode ("container-" + i, node, {_ classList add "container"}))
	end
	# We retrieve the symbol with the given name
	var s = STATE symbols [symbol]
	if s
		renderDescription (s)
	else
		console warn ("smalldoc.show: Cannot find symbol `" + symbol + "`")
	end
@end


@function onHashChange event
	show (window location hash substr 1)
@end

# -----------------------------------------------------------------------------
#
# RENDERERS
#
# -----------------------------------------------------------------------------

@function renderDescription element
	let node = document getElementById "description"
	while node firstChild
		node removeChild (node firstChild)
	end
	# Description
	let parents = element id split "." ; let name = parents pop ()
	node appendChild (html div (
		{_:"overview"}
		html h1 (
			html span ({_:"type"}, _getGroup (element))
			html span ({_:"parents"}, parents map {
				html span ({_:"parent name"}, _)
			})
			html span ({_:"name"}, element name or name)
		)
	))
	# Representation
	if element representation
		let r = html div ({_:"representation"})
		r innerHTML = element representation
		node appendChild (r)
	end
	# Documentation
	let d = html div ({_:"documentation"})
	d innerHTML = element documentation or "<div class='undocumented'>Undocumented</div>"
	node appendChild (d)
	# Relations
	let n = renderRelations (element)
	console log (n)
	node appendChild (n)
@end

@function renderName:Element name:String, type:String=Undefined
| Renders a symbol name.
	let names  = (name or "__root__") split "."
	let parent = if names length > 1 -> names[names length - 2] | "__root__"
	let n      = names pop ()
	return html div (
		{_:"name", data-type:type, data-name:name}
		html span {_:"type"}
		html span (
			{_:"parents", data-count:"" + parent length}
			names map {html span ({_:"parent"}, _)}
		)
		html span ({_:"symbol"}, n)
	)
@end

@function renderContainer data, name, type=None
	let names  = (data id or data name or "__root__") split "."
	let parent = if names length > 1 -> names[names length - 2] | "__root__"
	type       = type or data type or (if name == "__root__" -> "root" | "generic")
	return _addContainer (html div (
		{_:"container",data-type:type, id:data id or data name or "__root__"}
		html div (
			{_:"title"}
			html a (
				{href:"#" + parent}
				renderName (name, type)
			)
		)
		_getGroups (data children) map {renderGroup (_[1], _[0])}
	))
@end

@function renderGroup slots, name
	return html div (
		{_:"group"}
		html div ({_:"title",data-key:name split " " join "-" toLowerCase()}, name)
		renderSlots (slots)
	)
@end

@function renderSlots slots
	return html ul (
		{_:"slots"}
		slots map {s|
			var a = _[1] children and renderContainer (_[1], _[1] id or _[0])
			var b = {_|STATE symbols [s[1] id or s[0]] = s[1]}()
			html div (
				{_:"slot" + (if s[1] documentation -> "" | " undocumented"), data-type:s[1] type, id:"slot:" + (s[1] id or s[0])}
				html a (
					{href:"#" + s[1] id or s[0]}
					renderName (s[0], s[1] type)
				)
			)
		}
	)
@end

@function renderRelations element
	let keys = []
	let d    = (element relations or []) reduce ({r,e|
		let k = e[0]
		if keys indexOf (k) == -1 -> keys push (k)
		r[k] ?= []
		r[k] push (e)
		r
	}, {})
	return html div (
		{_:"relations"}
		keys sort () map {
			html div (
				{_:"relation",data-type:_}
				html h2 (_)
				html ul (
					d[_] map {
						html li (renderRelation(_))
					}
				)
			)
		}
	)
@end

@function renderRelation r
	let name = r[0]
	if name == "defined"
		let s = STATE symbols [r[1]]
		return html span (
			{_:"defined"}
			html span (
				{_:"name", data-type:_getGroup(s)}
				html a ({href:"#" + r[1]}, r[1])
			)
		)
	elif name == "defines"
		let k = r[1]
		let v = STATE symbols [r[2]]
		return html span (
			{_:"defines"}
			html span (
				{_:"name", data-type:_getGroup(s)}
				k
				"="
				html a ({href:"#" + r[1]}, r[1])
			)
		)

	else
		return None
	end
@end

# -----------------------------------------------------------------------------
#
# HELPERS
#
# -----------------------------------------------------------------------------

@function _getGroup element
	return GROUPS find {(element tags or []) indexOf (_) > -1} or element type or "value"
@end

@function _getGroups elements:List, sort=True
	let g =	elements reduce ({r,e|
		let k = _getGroup (e[1])
		r[k] ?= []
		r[k] push (e)
		r
	}, {})
	let r = GROUPS reduce ({r,e|
		let l = g[e]
		if typeof (l) == "object"
			if sort -> l sort {a,b|return a[0] localeCompare (b[0])}
			r push [e, l]
		end
		r
	}, [])
	return r
@end

@function _addContainer node, scope="hidden"
	let parent = document getElementById (scope)
	if parent firstChild
		parent insertBefore (node, parent firstChild)
	else
		parent appendChild (node)
	end
	return node
@end

@function _clearContainers
	let node   = document getElementById "containers"
	let hidden = document getElementById "hidden"
	while STATE active length > 0
		STATE active pop () classList remove "active"
	end
	while node firstChild
		hidden appendChild (node firstChild)
	end
@end

@function _showContainer name
	let node = document getElementById (name)
	let slot = document getElementById ("slot:" + name)
	if slot
		STATE active push (slot)
		slot classList add "active"
	end
	if node
		document getElementById "containers" appendChild (node)
	else
		console warn ("smalldoc: cannot find container `" + name + "`")
	end
	return name
@end

# EOF
