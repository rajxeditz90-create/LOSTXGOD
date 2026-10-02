import base64
import zlib

_KEY = bytes.fromhex("4d454e54414c5f5041594c4f41445f5631")
# We will read payload from a string
_PAYLOAD = open("payload_str.txt").read().strip()
_DATA = base64.b85decode(_PAYLOAD.encode("ascii"))
_DATA = bytes(b ^ _KEY[i % len(_KEY)] for i, b in enumerate(_DATA))
_SOURCE = zlib.decompress(_DATA).decode("utf-8", errors="replace")
with open("decrypted_code.py", "w") as f:
    f.write(_SOURCE)
print("Decrypted successfully, length:", len(_SOURCE))
