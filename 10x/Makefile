SHELL = /bin/bash
NAME = 10x
PYTHON ?= python3
SQUEEZED_DPI ?= 200
SOURCES = $(wildcard *.tex *.bib *.png) mkpdf.sh

.PHONY: all clean release check FORCE
all: $(NAME).pdf $(NAME)-squeezed.pdf

$(NAME).pdf: build/$(NAME).pdf
	cp $< $@

$(NAME)-squeezed.pdf: build/$(NAME)-squeezed.pdf
	cp $< $@

build/$(NAME).pdf: $(SOURCES) | build
	$(SHELL) mkpdf.sh $(NAME).tex

# Update the timestamp only when the requested resolution changes.
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

clean:
	rm -rf build .tempdir
	rm -f $(NAME).pdf $(NAME)-squeezed.pdf

release: all
	rm -f $(NAME).zip
	rm -rf .tempdir
	mkdir -p .tempdir/$(NAME)
	cp $(NAME).pdf $(NAME)-squeezed.pdf Makefile $(NAME).tex structure.tex .tempdir/$(NAME)/
	cd .tempdir && zip -r ../$(NAME).zip $(NAME)
	rm -rf .tempdir
