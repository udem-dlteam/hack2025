#!/bin/sh

VENV="venv"
PYTHON3="python3"

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd $ROOT_DIR


# use a Python venv
if [ ! -e "$VENV" ] ; then
    echo "===== creating a python venv"
    ${PYTHON3} -m venv "${VENV}"
fi
source "$VENV/bin/activate"


if ! pip show requests > /dev/null 2>&1; then
    echo "===== installing requests"
    pip install requests
fi


PATH_FILE="../parcours/LOWI_08_circuit/LOWI_08_circuit.csv"

CMD="${PYTHON3} radar.py $PATH_FILE"

echo "Running: ${CMD}"

eval ${CMD}
