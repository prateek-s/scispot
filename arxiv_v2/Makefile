PDF = paper.pdf
DRAFT = draft.pdf
TEX := $(wildcard *.tex) 
BIB := $(wildcard *.bib)

UNAME := $(shell uname)


PDFLATEX_ARGS = -shell-escape -interaction nonstopmode

.PHONY : default

default : $(PDF)


$(PDF) : $(TEX) $(BIB)
	-pdflatex $(PDFLATEX_ARGS) paper
	-pdflatex $(PDFLATEX_ARGS) paper
	-bibtex paper
	-pdflatex $(PDFLATEX_ARGS) paper
	-pdflatex $(PDFLATEX_ARGS) paper
	-cp paper.pdf paper-bloated.pdf

#ifeq ($(UNAME), Darwin)
#	open paper.pdf
#endif

draft : $(PDF)
	mv $(PDF) $(DRAFT)

compress : $(PDF)
	gs -q -dBATCH -sOutputFile=paper.pdf -dNOPAUSE -sDEVICE=pdfwrite  -dSubsetFonts=true -dCompressFonts=true -f paper-bloated.pdf 


clean:
	rm -f $(PS) $(PDF) *.dvi *.log *.aux *.bbl *.blg *.ent *.synctex.gz
