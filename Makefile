PROJECT      =smalldoc
SOURCES_SJS  =$(wildcard src/smalldoc/templates/*.sjs)
SOURCES_PCSS =$(wildcard src/smalldoc/templates/*.pcss)
SOURCES_PAML =$(wildcard src/smalldoc/templates/*.paml)
BUILD_EXTRA  =$(SOURCES_SJS:%.sjs=%.js) $(SOURCES_SJS:%.pcss=%.css) $(SOURCES_SJS:%.paml=%.html)
DIST_EXTRA   =$(BUILD_EXTRA)

%.html: %.paml
	paml $< > $@

%.css: %.pcss
	pcss $< > $@

%.js: %.sjs
	sugar -cljs $< > $@

include Makefile.pymodule
#EOF
