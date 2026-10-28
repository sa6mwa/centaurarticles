SHELL = /bin/bash
.NOTPARALLEL:
NAME = coordination-trap
PYTHON ?= python3
SQUEEZED_DPI ?= 200
LOGOS = $(patsubst %.svg,%.pdf,$(wildcard assets/*.svg))
COVER_TYPE = assets/cover-type.pdf
SOURCES = $(wildcard *.tex *.bib *.png) abstract.tex body.tex $(LOGOS) $(COVER_TYPE) mkpdf.sh

abstract.tex: $(NAME).md manuscript.lua
	pandoc $< --from=markdown --to=latex --natbib --lua-filter=manuscript.lua -M part=abstract --output=$@

body.tex: $(NAME).md manuscript.lua
	pandoc $< --from=markdown --to=latex --natbib --lua-filter=manuscript.lua -M part=body --output=$@

assets/%.pdf: assets/%.svg
	rsvg-convert --format=pdf --output=$@ $<

$(COVER_TYPE): cover-type.svg assets/fontconfig.conf assets/fonts/BebasNeue-Regular.ttf | build
	FONTCONFIG_FILE="$(CURDIR)/assets/fontconfig.conf" rsvg-convert --format=pdf --output=$@ $<

.DEFAULT_GOAL := all
.PHONY: all clean release check FORCE
all: $(NAME).pdf $(NAME)-squeezed.pdf

$(NAME).pdf: build/$(NAME).pdf
	cp $< $@

$(NAME)-squeezed.pdf: build/$(NAME)-squeezed.pdf
	cp $< $@

build/$(NAME).pdf: $(SOURCES) | build
	$(SHELL) mkpdf.sh $(NAME).tex

build/squeezed-dpi: FORCE | build
	@printf '%s\n' '$(SQUEEZED_DPI)' > $@.tmp
	@cmp -s $@.tmp $@ || cp $@.tmp $@
	@rm -f $@.tmp

build/$(NAME)-squeezed.pdf: build/$(NAME).pdf $(SOURCES) squeeze.py verify_pdfs.py build/squeezed-dpi
	$(PYTHON) squeeze.py build/$(NAME).pdf build/squeezed --dpi $(SQUEEZED_DPI)
	cd build/squeezed && $(SHELL) ../../mkpdf.sh $(NAME).tex
	$(PYTHON) verify_pdfs.py build/$(NAME).pdf build/squeezed/build/$(NAME).pdf
	cp build/squeezed/build/$(NAME).pdf $@

build:
	mkdir -p $@

check: all
	$(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) verify_pdfs.py $(NAME).pdf $(NAME)-squeezed.pdf
	$(PYTHON) verify_essay.py

clean:
	rm -rf build .tempdir
	rm -f $(NAME).pdf $(NAME)-squeezed.pdf $(LOGOS) $(COVER_TYPE) abstract.tex body.tex

release: check
	rm -f $(NAME).zip
	rm -rf .tempdir
	mkdir -p .tempdir/$(NAME)
	cp $(NAME).pdf $(NAME)-squeezed.pdf *.md *.bib *.tex *.lua *.py *.sh *.png *.svg Makefile .tempdir/$(NAME)/
	cp -r assets illustrations tests .tempdir/$(NAME)/
	cd .tempdir && zip -r ../$(NAME).zip $(NAME) -x '*/__pycache__*'
	rm -rf .tempdir
