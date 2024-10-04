#!/usr/bin/env bash
set -euo pipefail

python -m mypy ./src
python -m pyright ./src
python -m pytest -vv
