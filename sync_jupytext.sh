#!/bin/bash

# f00_xxx.ipynb 형식만 자동 동기화 설정
for f in *.ipynb; do
    base=$(basename "$f" .ipynb)
    if [[ $base =~ ^f[0-9]{1,2}_.+ ]]; then
        echo "🔄 Pairing $f with $base.py"
        jupytext --set-formats ipynb,py:percent "$f"
    fi
done
