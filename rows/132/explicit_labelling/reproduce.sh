#!/usr/bin/env bash
# Standard-library reproduction of the family 132 explicit-labelling checks.
set -euo pipefail
cd "$(dirname "$0")"
CONTROLS="bound-too-small constant-label epsilon-below-57 parity-label"
(cd source && sha256sum -c SHA256SUMS)
python3 -m unittest discover -s . -p 'test_*.py'
python3 -O -m unittest discover -s . -p 'test_*.py'
out=$(python3 check.py)
printf '%s\n' "$out"
printf '%s\n' "$out" | cmp -s - output.txt || {
    echo "ERROR: check.py output differs from output.txt" >&2; exit 1; }
for control in $CONTROLS; do
    for flag in "" -O; do
        status=0
        out=$(python3 $flag check.py --negative-control "$control") || status=$?
        if [ "$status" -ne 1 ] || ! grep -q '^RESULT: fails$' <<< "$out"; then
            echo "ERROR: negative control $control ${flag:-(normal)} exited $status without RESULT: fails" >&2
            exit 1
        fi
    done
done
echo 'RESULT: family 132 explicit-labelling checks and rejection controls reproduced'
