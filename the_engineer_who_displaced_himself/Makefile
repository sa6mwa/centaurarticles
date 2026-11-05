.NOTPARALLEL:
NAME = the-engineer-who-displaced-himself
TECTONIC ?= tectonic
.PHONY: all check render clean
all: $(NAME).pdf

$(NAME).pdf: $(NAME).tex cover.tex editorial-layout.tex fonts/Anton-Regular.ttf fonts/Barlow-Medium.ttf manuscript.tex notes.tex structure.tex illustrations/cover.png illustrations/interview-comic.png illustrations/coordination-shift-cover.png
	mkdir -p build/cache
	XDG_CACHE_HOME="$(CURDIR)/build/cache" $(TECTONIC) --untrusted --keep-logs --outdir build $(NAME).tex
	cp build/$(NAME).pdf $@

check: all
	pdfinfo $(NAME).pdf > build/pdf-info.txt
	pdftotext -layout $(NAME).pdf build/essay.txt
	test -s build/essay.txt
	! grep -E "Overfull|Undefined control sequence|undefined references|Missing character|LaTeX Font Warning" build/$(NAME).log

render: all
	mkdir -p build/render
	pdftoppm -scale-to 1400 -png $(NAME).pdf build/render/page

clean:
	rm -rf build
	rm -f $(NAME).pdf
