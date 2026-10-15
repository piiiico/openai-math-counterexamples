"""Replay the finite channel certificate against its separately verified tensor predecessor."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from time import monotonic

from .checker import ChannelCertificateError, verify_saved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tensor", type=Path, help="the predecessor tensor/certificate.json")
    parser.add_argument("--certificate", type=Path, default=Path(__file__).with_name("certificate.json"))
    args = parser.parse_args()
    start = monotonic()
    try:
        source = args.tensor.read_bytes()
        certificate = args.certificate.read_bytes()
        result = verify_saved(json.loads(source), json.loads(certificate))
        result.update(tensor_file_sha256=hashlib.sha256(source).hexdigest(),
                      certificate_file_sha256=hashlib.sha256(certificate).hexdigest(),
                      elapsed_seconds=round(monotonic() - start, 6))
    except (ChannelCertificateError, ValueError, TypeError, KeyError, OSError, IndexError) as error:
        print(json.dumps(dict(status="not_certified", reason=str(error))))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
