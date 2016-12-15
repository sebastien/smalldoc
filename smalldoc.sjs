@module smalldoc
| Renders `smalldoc` JSON data into a Smalltalk-like documentation browser. The resulting
| document will ony work on modern browsers.

@shared DATA    = None
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

@function load path="data.json"
	fetch (path) then {_ json () then (setup)}
@end

@function setup data
	DATA = data
	render (data)
	window addEventListener ("hashchange", onHashChange)
	onHashChange ()
@end

@function render data
	renderContainer (_, "Smalldoc")
@end

@function show symbol
	_clearContainers ()
	_showContainer "__root__"
	let n = (symbol or "") split "."
	n reduce ({r,e|_showContainer (if r -> r + "." + e | e)}, "")
	# NOTE: Removed for now
	# let c = n length
	# var node = document getElementById "containers"
	# while node childNodes length < 2
	# 	node appendChild (document getElementById ("container-" + (3 - node childNodes length)))
	# end
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
	let d = html div ({_:"documentation"})
	d innerHTML = element documentation or "<div class='undocumented'>Undocumented</div>"
	node appendChild (d)
@end

@function renderContainer data, name
	let names  = (data id or data name or "__root__") split "."
	let parent = if names length > 1 -> names[names length - 2] | "__root__"
	return _addContainer (html div (
		{_:"container",data-type:data type or "generic", id:data id or data name or "__root__"}
		html div ({_:"name"}, html a ({href:"#" + parent}, name))
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
				{_:"slot" + (if _[1] documentation -> "" | " undocumented"), data-type:_[1] type, id:"slot:" + (_[1] id or _[0])}
				html a (
					{href:"#" + _[1] id or _[0]}
					_[0]
				)
			)
		}
	)
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

# -----------------------------------------------------------------------------
#
# INIT
#
# -----------------------------------------------------------------------------

load ()

# EOF
