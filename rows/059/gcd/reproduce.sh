#!/usr/bin/env bash
# Alexander Richard Towell, with substantial OpenAI Codex assistance. MIT.
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c source/SHA256SUMS
python3 -m unittest discover -s . -p 'test_*.py'
python3 -O -m unittest discover -s . -p 'test_*.py'
out=$(python3 check.py)
printf '%s\n' "$out"
printf '%s\n' "$out" | cmp -s - output.txt || {
    echo 'ERROR: output differs from committed exact result' >&2; exit 1;
}
for control in coefficient wrong-ratio reverse-sign invalid-index wrong-d; do
    for mode in normal optimized; do
        flags=()
        if [ "$mode" = optimized ]; then flags=(-O); fi
        status=0
        out=$(python3 "${flags[@]}" check.py --negative-control "$control" 2>&1) || status=$?
        if [ "$status" -ne 1 ] || [[ "$out" != 'RESULT: fails -- '* ]]; then
            echo "ERROR: $control/$mode did not reject with the expected failure result" >&2
            exit 1
        fi
        printf '%s: %s\n' "$control/$mode" "$out"
    done
done
echo 'RESULT: Family 059 exact GCD cancellation and rejecting controls reproduced'
