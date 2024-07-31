#!/usr/bin/env bash
set -euo pipefail

python -m mypy .
python -m pyright .
python -m pytest -vv
