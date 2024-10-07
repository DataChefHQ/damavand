#!/usr/bin/env bash
set -euo pipefail

python -m mypy ./src
python -m mypy ./tests
python -m pytest -vv
