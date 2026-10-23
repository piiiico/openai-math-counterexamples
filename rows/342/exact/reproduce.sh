#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c source/SHA256SUMS
python3 -m unittest discover -s . -p 'test_*.py'
python3 -O -m unittest discover -s . -p 'test_*.py'
python3 check.py
for control in eta-factor derivative-support taming-amplitude; do
    if python3 -O check.py --negative-control "$control"; then
        echo "ERROR: negative control accepted: $control" >&2
        exit 1
    else
        status=$?
        if [ "$status" -ne 1 ]; then
            echo "ERROR: unexpected failure status $status" >&2
            exit 1
        fi
    fi
done
echo 'RESULT: exact torus packet and rejection controls reproduced'
