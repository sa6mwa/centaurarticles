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
BASENAME=$(basename "$FILE" .tex)
PASS=0
while [[ $PASS -lt $MAX_PASSES ]]; do
  pdflatex -interaction=nonstopmode -shell-escape --output-format=pdf --output-directory=$OUTDIR "$FILE"
  if grep -q "Please (re)run BibTeX" "$OUTDIR/$BASENAME.log"; then
    echo "Rerunning bibtex..."
    pushd $OUTDIR
    bibtex $BASENAME
    popd
    PASS=$((PASS+1))
  elif grep -qE "Rerun to get|Please rerun LaTeX" "$OUTDIR/$BASENAME.log"; then
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
