"""Replay the tensor certificate against a supplied integer pencil."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from time import monotonic

from .checker import TensorCertificateError, verify_saved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pencil", type=Path, help="the geometric predecessor's pencil.json")
    parser.add_argument("--certificate", type=Path, default=Path(__file__).with_name("certificate.json"))
    args = parser.parse_args()
    start = monotonic()
    try:
        source = args.pencil.read_bytes()
        certificate = args.certificate.read_bytes()
        result = verify_saved(json.loads(source)["matrices"], json.loads(certificate))
        result.update(pencil_file_sha256=hashlib.sha256(source).hexdigest(),
                      certificate_file_sha256=hashlib.sha256(certificate).hexdigest(),
                      elapsed_seconds=round(monotonic() - start, 6))
    except (TensorCertificateError, ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({"status": "not_certified", "reason": str(error)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
