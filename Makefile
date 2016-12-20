PROJECT      =smalldoc
SOURCES_SJS  =$(wildcard src/smalldoc/templates/*.sjs)
SOURCES_PCSS =$(wildcard src/smalldoc/templates/*.pcss)
SOURCES_PAML =$(wildcard src/smalldoc/templates/*.paml)
BUILD_EXTRA  =$(SOURCES_SJS:%.sjs=%.js) $(SOURCES_PCSS:%.pcss=%.css) $(SOURCES_PAML:%.paml=%.html)
DIST_EXTRA   =$(BUILD_EXTRA)

include Makefile.pymodule

%.html: %.paml
	@echo "$(GREEN)📝  $@ [PAML]$(RESET)"
	@paml $< | sed 's|\.sjs|\.js|g;s|\.pcss|\.css|g' > $@
	@chmod -w $@

%.css: %.pcss
	@echo "$(GREEN)📝  $@ [PCSS]$(RESET)"
	@pcss $< | cssmin > $@
	@chmod -w $@

%.js: %.sjs
	@echo "$(GREEN)📝  $@ [SJS]]$(RESET)"
	@sugar -cljs $< | closure-compiler > $@
	@chmod -w $@

#EOF
