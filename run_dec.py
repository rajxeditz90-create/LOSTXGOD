import os
import re
import zlib
import base64

_KEY = bytes.fromhex("4d454e54414c5f5041594c4f41445f5631")
_PAYLOAD = open("/tmp/payload_raw.txt").read().strip()
_DATA = base64.b85decode(_PAYLOAD.encode("ascii"))
_DATA = bytes(b ^ _KEY[i % len(_KEY)] for i, b in enumerate(_DATA))
_SOURCE = zlib.decompress(_DATA).decode("utf-8")
with open("/tmp/decrypted_bot.py", "w") as f:
    f.write(_SOURCE)
print("Decoded length:", len(_SOURCE))
print("First 500 chars:")
print(_SOURCE[:500])
