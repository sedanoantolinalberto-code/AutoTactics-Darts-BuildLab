"""Isolated B39 minimal repair. The B38 original source payload stays immutable.

Apply only to the verified extraction of windows_joblist_launcher.py, and
refuse mismatched preimages. Does not modify any release, main or supervisor.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"native"/"windows_joblist_launcher.py"
PRE_SHA="b0ebd62ea68821dd93560ea39cc0ca91841f1c50eb4dc279f85b2f26a6a66237"
POST_SHA="51885aa5b2417b877affdc0a440c6431a0d155063aa5a2f0c15f5e747c964f6c"
OLD="return int(h.value if hasattr(h, 'value') else h or 0)"
NEW="value=h.value if hasattr(h, 'value') else h\n        return int(value or 0)"

def main():
    pre=SOURCE.read_bytes()
    assert hashlib.sha256(pre).hexdigest()==PRE_SHA,"refuse patch on unknown B38 source"
    text=pre.decode("utf-8")
    assert text.count(OLD)==1,"patch anchor absent or ambiguous"
    patched=text.replace(OLD,NEW,1).encode("utf-8")
    assert hashlib.sha256(patched).hexdigest()==POST_SHA,"post-patch hash mismatch"
    SOURCE.write_bytes(patched)
    print(json.dumps({"status":"B39_REVIEW_ONLY_PATCHED_FROM_B38",
      "file":SOURCE.name,"pre_sha256":PRE_SHA,"post_sha256":POST_SHA},sort_keys=True))
if __name__=="__main__":main()
