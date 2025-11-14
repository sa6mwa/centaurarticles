#!/bin/bash
set -euo pipefail
FILE="$1"
MAX_PASSES=5
OUTDIR="build"
if [[ -z "$FILE" ]]; then
  echo "Usage $0 file.tex"
  exit 1
fi
if [[ ! -d "$OUTDIR" ]]; then
  mkdir "$OUTDIR"
fi

# Make sure any local .bib files are visible to BibTeX when it runs from the build dir
shopt -s nullglob
for bibfile in *.bib; do
  cp "$bibfile" "$OUTDIR"/
done
shopt -u nullglob
BASENAME=$(basename "$FILE" .tex)
PASS=0
while [[ $PASS -lt $MAX_PASSES ]]; do
  pdflatex -interaction=nonstopmode -shell-escape --output-format=pdf --output-directory=$OUTDIR "$FILE"
  need_bibtex=false
  if [[ ! -s "$OUTDIR/$BASENAME.bbl" ]]; then
    need_bibtex=true
  elif grep -q "Please (re)run BibTeX" "$OUTDIR/$BASENAME.log"; then
    need_bibtex=true
  fi

  if [[ "$need_bibtex" == true ]]; then
    echo "Running bibtex to update bibliography..."
    pushd $OUTDIR > /dev/null
    BIBINPUTS="../:${BIBINPUTS:-}" BSTINPUTS="../:${BSTINPUTS:-}" bibtex $BASENAME
    popd > /dev/null
    PASS=$((PASS+1))
    continue
  fi

  if grep -qE "Rerun to get|Please rerun LaTeX" "$OUTDIR/$BASENAME.log"; then
    echo "Rerunning pdflatex for unresolved references..."
    PASS=$((PASS+1))
  else
    break
  fi
done
if [[ $PASS -eq $MAX_PASSES ]]; then
  echo "Reached maximum number of passes, check $OUTDIR/$BASENAME.log for issues."
  exit 1
fi
