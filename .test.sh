#!/usr/bin/env bash
set -euo pipefail

python -m mypy ./src
python -m pyright .
python -m pytest -vv
