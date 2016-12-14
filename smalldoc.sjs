@module smalldoc

@function load path="data.json"
	fetch (path) then {_ json () then (render)}
@end

@function render data
	renderContainer (_, "Smalldoc")
@end

@function addContainer node
	document getElementById "containers" appendChild (node)
	return node
@end

@function renderContainer data, name
	return addContainer (html div (
		{_:"container"}
		html div ({_:"name"}, name)
		renderGroup (data children, "Modules")
	))
@end

@function renderGroup slots, name
	return html div (
		{_:"group"}
		html div ({_:"title"}, name)
		renderSlots (slots)
	)
@end

@function renderSlots slots
	return html ul (
		{_:"slots"}
		slots map {
			_[1] children and renderContainer (_[1], _[1] id or _[0]) and False
			html div (
				{_:"slot", data-type:_[1] type}
				html a (
					{name:_[1] id or _[0]}
					_[0]
				)
			)
		}
	)
@end

load ()
