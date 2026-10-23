#!/usr/bin/env bash
# Standard-library reproduction. Set INDEPENDENT=1 to also run the SymPy implementation
# (needs uv; it pins sympy==1.14.0) and compare its hash of q.
set -euo pipefail
cd "$(dirname "$0")"
CONTROLS="H-coefficient derivation-value linear-coordinates linear-inverse e0-sign"
sha256sum -c source/SHA256SUMS
python3 -m unittest discover -s . -p 'test_*.py'
python3 -O -m unittest discover -s . -p 'test_*.py'
out=$(python3 check.py 2>/dev/null)
printf '%s\n' "$out"
printf '%s\n' "$out" | cmp -s - output.txt || {
    echo "ERROR: check.py output differs from output.txt" >&2; exit 1; }
for control in $CONTROLS; do
    for flag in "" -O; do
        status=0
        out=$(python3 $flag check.py --negative-control "$control" 2>/dev/null) || status=$?
        if [ "$status" -ne 1 ] || ! grep -q '^RESULT: fails$' <<< "$out"; then
            echo "ERROR: negative control $control ${flag:-(normal)} exited $status without RESULT: fails" >&2
            exit 1
        fi
    done
done
if [ "${INDEPENDENT:-0}" = 1 ]; then
    run() {  # run PYTHON_FLAG [SCRIPT_ARGS...]
        local flag=$1; shift
        uv run --quiet --no-project --with sympy==1.14.0 python3 $flag independent/independent_check.py "$@"
    }
    run "" 2>/dev/null | cmp -s - independent/output.txt || {
        echo "ERROR: independent output differs from independent/output.txt" >&2; exit 1; }
    pinned=$(sed -n 's/^EXPECTED_Q_SHA256 = "\([0-9a-f]*\)"$/\1/p' check.py)
    grep -q "sha256(q) = $pinned" independent/output.txt || {
        echo "ERROR: independent hash of q differs from check.py's pin" >&2; exit 1; }
    for control in $CONTROLS; do
        for flag in "" -O; do
            status=0
            run "$flag" --negative-control "$control" > /dev/null 2>&1 || status=$?
            [ "$status" -eq 1 ] || { echo "ERROR: independent control $control exited $status" >&2; exit 1; }
        done
    done
    echo 'independent SymPy implementation reproduced; hashes of q agree'
fi
echo 'RESULT: family 047 exact certificate and rejection controls reproduced'
