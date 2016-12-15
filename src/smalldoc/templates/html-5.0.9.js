
// START:UMD_MODULE_PREAMBLE
(function (global, factory) {
	if (typeof define === "function" && define.amd) {
		define(["exports"], factory);
	} else if (typeof exports !== "undefined") {
		factory(exports);
	} else {
		var mod = {exports: {}};
		factory(mod.exports);
		global.actual = mod.exports;
	}
})(this, function (exports) {
	Object.defineProperty(exports, "__esModule", {value: true});
	var html = exports; var __module__ = html;
// END:UMD_MODULE_PREAMBLE

__module__ = typeof(html) === undefined ? {} : html;
__module__.NAMESPACE=__module__.namespace=null;
__module__.NAMESPACES=__module__.namespaces={"svg": "http://www.w3.org/2000/svg", "html": "http://www.w3.org/1999/xhtml", "xlink": "http://www.w3.org/1999/xlink"};
__module__._=function(name, args){
	if (__module__.NAMESPACE){
		var node   = document.createElementNS(null, name);
	} else {
		var node   = document.createElement(name);
	}
	/* Appends the given value to the node */
	var append = function (node, value ) {
		if      ( value == undefined ) {
			return;
		}
		else if ( typeof(value) == "string" ) {
			node.appendChild(document.createTextNode(value));
		}
		else if ( typeof(value) == "object" && typeof(value.jquery) != "undefined" ) {
			for ( var j=0 ; j<value.length ; j++ )
			{ append(node, value[j]); }
		}
		else if ( typeof(value) == "object" && typeof(value.nodeType) != "undefined" ) {
			node.appendChild(value);
		}
		else if ( typeof(value) == "object" && value instanceof Array ) {
			for ( var j=0 ; j<value.length ; j++ )
			{ append(node, value[j]); }
		}
		else {
			var has_properties = false;
			for ( var k in value ) {
				var ns  = null;
				var dot = k.lastIndexOf(":");
				var v   = value[k];
				if (dot>=0) {
					ns = k.substr(0,dot);
					ns = __module__.NAMESPACES[ns] || ns;
					k  = k.substr(dot+1,k.length);
				}
				if ( k == "_" || k == "_class" || k == "klass" ) { k = "class" }
				if (ns) { node.setAttributeNS(ns, k, v); }
				else    { node.setAttribute  (    k, v); }
				has_properties = true;
			}
			if (!has_properties)
			{ node.appendChild(document.createTextNode("" + value)); }
		}
	}
	// Iterates through the arguments, and appends the content
	for ( var i = 0 ; i < args.length ; i ++ )
	{
		append(node, args[i]);
	}
	return node;
}
/* TAGS:START */
__module__.address=function(){return __module__._('address', arguments)};
__module__.applet=function(){return __module__._('applet', arguments)};
__module__.area=function(){return __module__._('area', arguments)};
__module__.a=function(){return __module__._('a', arguments)};
__module__.base=function(){return __module__._('base', arguments)};
__module__.basefont=function(){return __module__._('basefont', arguments)};
__module__.big=function(){return __module__._('big', arguments)};
__module__.blockquote=function(){return __module__._('blockquote', arguments)};
__module__.body=function(){return __module__._('body', arguments)};
__module__.br=function(){return __module__._('br', arguments)};
__module__.b=function(){return __module__._('b', arguments)};
__module__.caption=function(){return __module__._('caption', arguments)};
__module__.center=function(){return __module__._('center', arguments)};
__module__.cite=function(){return __module__._('cite', arguments)};
__module__.code=function(){return __module__._('code', arguments)};
__module__.dd=function(){return __module__._('dd', arguments)};
__module__.dfn=function(){return __module__._('dfn', arguments)};
__module__.dir=function(){return __module__._('dir', arguments)};
__module__.div=function(){return __module__._('div', arguments)};
__module__.dl=function(){return __module__._('dl', arguments)};
__module__.dt=function(){return __module__._('dt', arguments)};
__module__.em=function(){return __module__._('em', arguments)};
__module__.font=function(){return __module__._('font', arguments)};
__module__.form=function(){return __module__._('form', arguments)};
__module__.h1=function(){return __module__._('h1', arguments)};
__module__.h2=function(){return __module__._('h2', arguments)};
__module__.h3=function(){return __module__._('h3', arguments)};
__module__.h4=function(){return __module__._('h4', arguments)};
__module__.h5=function(){return __module__._('h5', arguments)};
__module__.h6=function(){return __module__._('h6', arguments)};
__module__.head=function(){return __module__._('head', arguments)};
__module__.hr=function(){return __module__._('hr', arguments)};
__module__.html=function(){return __module__._('html', arguments)};
__module__.img=function(){return __module__._('img', arguments)};
__module__.input=function(){return __module__._('input', arguments)};
__module__.isindex=function(){return __module__._('isindex', arguments)};
__module__.i=function(){return __module__._('i', arguments)};
__module__.kbd=function(){return __module__._('kbd', arguments)};
__module__.link=function(){return __module__._('link', arguments)};
__module__.li=function(){return __module__._('li', arguments)};
__module__.map=function(){return __module__._('map', arguments)};
__module__.menu=function(){return __module__._('menu', arguments)};
__module__.meta=function(){return __module__._('meta', arguments)};
__module__.ol=function(){return __module__._('ol', arguments)};
__module__.option=function(){return __module__._('option', arguments)};
__module__.param=function(){return __module__._('param', arguments)};
__module__.pre=function(){return __module__._('pre', arguments)};
__module__.p=function(){return __module__._('p', arguments)};
__module__.samp=function(){return __module__._('samp', arguments)};
__module__.script=function(){return __module__._('script', arguments)};
__module__.select=function(){return __module__._('select', arguments)};
__module__.small=function(){return __module__._('small', arguments)};
__module__.strike=function(){return __module__._('strike', arguments)};
__module__.strong=function(){return __module__._('strong', arguments)};
__module__.style=function(){return __module__._('style', arguments)};
__module__.sub=function(){return __module__._('sub', arguments)};
__module__.sup=function(){return __module__._('sup', arguments)};
__module__.table=function(){return __module__._('table', arguments)};
__module__.td=function(){return __module__._('td', arguments)};
__module__.textarea=function(){return __module__._('textarea', arguments)};
__module__.th=function(){return __module__._('th', arguments)};
__module__.title=function(){return __module__._('title', arguments)};
__module__.tr=function(){return __module__._('tr', arguments)};
__module__.tt=function(){return __module__._('tt', arguments)};
__module__.ul=function(){return __module__._('ul', arguments)};
__module__.u=function(){return __module__._('u', arguments)};
__module__['var']=__module__._var=function(){return __module__._('var', arguments)};
__module__.a=function(){return __module__._('a', arguments)};
__module__.abbr=function(){return __module__._('abbr', arguments)};
__module__.acronym=function(){return __module__._('acronym', arguments)};
__module__.address=function(){return __module__._('address', arguments)};
__module__.applet=function(){return __module__._('applet', arguments)};
__module__.area=function(){return __module__._('area', arguments)};
__module__.article=function(){return __module__._('article', arguments)};
__module__.aside=function(){return __module__._('aside', arguments)};
__module__.audio=function(){return __module__._('audio', arguments)};
__module__.b=function(){return __module__._('b', arguments)};
__module__.base=function(){return __module__._('base', arguments)};
__module__.basefont=function(){return __module__._('basefont', arguments)};
__module__.bdo=function(){return __module__._('bdo', arguments)};
__module__.big=function(){return __module__._('big', arguments)};
__module__.blockquote=function(){return __module__._('blockquote', arguments)};
__module__.body=function(){return __module__._('body', arguments)};
__module__.br=function(){return __module__._('br', arguments)};
__module__.button=function(){return __module__._('button', arguments)};
__module__.canvas=function(){return __module__._('canvas', arguments)};
__module__.caption=function(){return __module__._('caption', arguments)};
__module__.center=function(){return __module__._('center', arguments)};
__module__.cite=function(){return __module__._('cite', arguments)};
__module__.code=function(){return __module__._('code', arguments)};
__module__.col=function(){return __module__._('col', arguments)};
__module__.colgroup=function(){return __module__._('colgroup', arguments)};
__module__.command=function(){return __module__._('command', arguments)};
__module__.datalist=function(){return __module__._('datalist', arguments)};
__module__.dd=function(){return __module__._('dd', arguments)};
__module__.del=function(){return __module__._('del', arguments)};
__module__.details=function(){return __module__._('details', arguments)};
__module__.dfn=function(){return __module__._('dfn', arguments)};
__module__.dir=function(){return __module__._('dir', arguments)};
__module__.div=function(){return __module__._('div', arguments)};
__module__.dl=function(){return __module__._('dl', arguments)};
__module__.dt=function(){return __module__._('dt', arguments)};
__module__.em=function(){return __module__._('em', arguments)};
__module__.embed=function(){return __module__._('embed', arguments)};
__module__.fieldset=function(){return __module__._('fieldset', arguments)};
__module__.figcaption=function(){return __module__._('figcaption', arguments)};
__module__.figure=function(){return __module__._('figure', arguments)};
__module__.font=function(){return __module__._('font', arguments)};
__module__.footer=function(){return __module__._('footer', arguments)};
__module__.form=function(){return __module__._('form', arguments)};
__module__.frame=function(){return __module__._('frame', arguments)};
__module__.frameset=function(){return __module__._('frameset', arguments)};
__module__.h1=function(){return __module__._('h1', arguments)};
__module__.head=function(){return __module__._('head', arguments)};
__module__.header=function(){return __module__._('header', arguments)};
__module__.hgroup=function(){return __module__._('hgroup', arguments)};
__module__.hr=function(){return __module__._('hr', arguments)};
__module__.html=function(){return __module__._('html', arguments)};
__module__.i=function(){return __module__._('i', arguments)};
__module__.iframe=function(){return __module__._('iframe', arguments)};
__module__.img=function(){return __module__._('img', arguments)};
__module__.input=function(){return __module__._('input', arguments)};
__module__.ins=function(){return __module__._('ins', arguments)};
__module__.keygen=function(){return __module__._('keygen', arguments)};
__module__.kbd=function(){return __module__._('kbd', arguments)};
__module__.label=function(){return __module__._('label', arguments)};
__module__.legend=function(){return __module__._('legend', arguments)};
__module__.li=function(){return __module__._('li', arguments)};
__module__.link=function(){return __module__._('link', arguments)};
__module__.map=function(){return __module__._('map', arguments)};
__module__.mark=function(){return __module__._('mark', arguments)};
__module__.menu=function(){return __module__._('menu', arguments)};
__module__.meta=function(){return __module__._('meta', arguments)};
__module__.meter=function(){return __module__._('meter', arguments)};
__module__.nav=function(){return __module__._('nav', arguments)};
__module__.noframes=function(){return __module__._('noframes', arguments)};
__module__.noscript=function(){return __module__._('noscript', arguments)};
__module__.object=function(){return __module__._('object', arguments)};
__module__.ol=function(){return __module__._('ol', arguments)};
__module__.optgroup=function(){return __module__._('optgroup', arguments)};
__module__.option=function(){return __module__._('option', arguments)};
__module__.output=function(){return __module__._('output', arguments)};
__module__.p=function(){return __module__._('p', arguments)};
__module__.param=function(){return __module__._('param', arguments)};
__module__.pre=function(){return __module__._('pre', arguments)};
__module__.progress=function(){return __module__._('progress', arguments)};
__module__.q=function(){return __module__._('q', arguments)};
__module__.rp=function(){return __module__._('rp', arguments)};
__module__.rt=function(){return __module__._('rt', arguments)};
__module__.ruby=function(){return __module__._('ruby', arguments)};
__module__.s=function(){return __module__._('s', arguments)};
__module__.samp=function(){return __module__._('samp', arguments)};
__module__.script=function(){return __module__._('script', arguments)};
__module__.section=function(){return __module__._('section', arguments)};
__module__.select=function(){return __module__._('select', arguments)};
__module__.small=function(){return __module__._('small', arguments)};
__module__.source=function(){return __module__._('source', arguments)};
__module__.span=function(){return __module__._('span', arguments)};
__module__.strike=function(){return __module__._('strike', arguments)};
__module__.strong=function(){return __module__._('strong', arguments)};
__module__.style=function(){return __module__._('style', arguments)};
__module__.sub=function(){return __module__._('sub', arguments)};
__module__.summary=function(){return __module__._('summary', arguments)};
__module__.sup=function(){return __module__._('sup', arguments)};
__module__.table=function(){return __module__._('table', arguments)};
__module__.tbody=function(){return __module__._('tbody', arguments)};
__module__.td=function(){return __module__._('td', arguments)};
__module__.textarea=function(){return __module__._('textarea', arguments)};
__module__.tfoot=function(){return __module__._('tfoot', arguments)};
__module__.th=function(){return __module__._('th', arguments)};
__module__.thead=function(){return __module__._('thead', arguments)};
__module__.time=function(){return __module__._('time', arguments)};
__module__.title=function(){return __module__._('title', arguments)};
__module__.tr=function(){return __module__._('tr', arguments)};
__module__.tt=function(){return __module__._('tt', arguments)};
__module__.u=function(){return __module__._('u', arguments)};
__module__.ul=function(){return __module__._('ul', arguments)};
__module__['var']=__module__._var=function(){return __module__._('var', arguments)};
__module__.video=function(){return __module__._('video', arguments)};
__module__.wbr=function(){return __module__._('wbr', arguments)};
__module__.xmp=function(){return __module__._('xmp', arguments)};
/* TAGS:END */

// START:UMD_MODULE_POSTAMBLE
Object.assign(exports, __module__);
if (typeof extend !== "undefined") {extend.module("html", __module__)}
if (typeof window !== "undefined") {window.html = __module__;}
return exports;
})
// END:UMD_MODULE_POSTAMBLE

