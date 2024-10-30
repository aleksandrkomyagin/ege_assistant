#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

alembic -c /bot/ege_assistant_bot/config/alembic.ini upgrade head

python /bot/ege_assistant_bot/main.py