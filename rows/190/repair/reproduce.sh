#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c source/SHA256SUMS
python3 -m unittest discover -s . -p 'test_*.py'
python3 -O -m unittest discover -s . -p 'test_*.py'
python3 repair.py
python3 independent.py
for control in truncate weaken witness; do
    if python3 -O repair.py --negative-control "$control"; then
        echo "ERROR: accepted negative control $control" >&2
        exit 1
    else
        status=$?
        test "$status" -eq 1
    fi
done
if python3 -O independent.py --negative-control; then
    echo 'ERROR: independent mutation accepted' >&2
    exit 1
else
    status=$?
    test "$status" -eq 1
fi
echo 'RESULT: repair packet, independent enumeration and rejecting controls reproduced'
