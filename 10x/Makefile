SHELL = /bin/bash
NAME = 10x
#PLANTUML=/usr/share/plantuml/plantuml.jar

all: $(NAME).pdf

.PHONY: clean
clean:
	rm -rf build
	rm -rf .tempdir

$(NAME).pdf: build
	#cp refs.bib build/
	#cd puml && java -jar $(PLANTUML) -teps operating-rhythm.puml
	$(SHELL) mkpdf.sh $(NAME).tex

build:
	mkdir build

.PHONY: release
release: $(NAME).pdf
	rm -f $(NAME).zip
	rm -rf .tempdir
	mkdir -p .tempdir/$(NAME)
	cp *.pdf Makefile $(NAME).tex structure.tex build/$(NAME).pdf .tempdir/$(NAME)/
	cd .tempdir && zip -r ../$(NAME).zip $(NAME)
	rm -rf .tempdir
