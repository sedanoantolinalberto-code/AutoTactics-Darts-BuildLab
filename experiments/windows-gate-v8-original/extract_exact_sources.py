"""Reconstruct only the 11 original B23-B25 source files from a pinned XZ payload.

The payload was made by concatenating UTF-8 source files using name\\0length\\n
headers and compressing with LZMA/XZ. It is not executable until checked.
"""
from __future__ import annotations
import base64
import hashlib
import json
import lzma
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXPECTED_PAYLOAD_SHA256="6327ae2507b5c899846a8e6f05449111f080d03a043bb5ffff15cb545735286b"
EXPECTED={
 "engineyt_snapshot_b03.py":"5dbe18cc3d64a877859e53b2b4031019b09e9fed5a78f5cd978b15f9bed4f438",
 "engineyt_snapshot_b04.py":"4b5f93738de4a02dfb04974874aa9885ae385894a017a2cc225725949bee1154",
 "supervisor_b09_hardened.py":"4764c26da86e7f199bef001d0e0c2d65f9bea04bbe8c7820d81e1ebbdf34564a",
 "windows_atomic_launcher.py":"900a4a637fc2c046d06a21f8c20164eba7df15ed7619d1ae15f0e4402bebac40",
 "windows_gate_v2.py":"7cfcaa9911b7bff18d1c5970e4918625954d0b56b0c3cf40d5de494e4925befa",
 "windows_gate_v3.py":"3abab2e3816c22ed5644e74fe66aa2b314f2e714eda3156141595e6a38dd6529",
 "windows_gate_v4.py":"51705c7e25a581192ec2d913ca2304b0fe6f91dde00990ef209fad0dc536cce8",
 "windows_gate_v6.py":"2f839fcdd75268c79ffc3f8b04d02f6be38b268960cf70c8a45bda42c1d6f264",
 "windows_gate_v7.py":"1e7d58df5a571c33516cab58c544cacf572cda5de3f86b42940b5a1a7b781aae",
 "windows_gate_v8.py":"6bdaf2efe6f0abf160c1c8e880d70b18595ae0f747f194449d4b15e02407efe0",
 "windows_joblist_launcher.py":"b0ebd62ea68821dd93560ea39cc0ca91841f1c50eb4dc279f85b2f26a6a66237"
}

def main():
    b64="".join((HERE/"v8_exact_sources.b64.txt").read_text(encoding="ascii").split())
    blob=base64.b64decode(b64,validate=True)
    assert len(blob)==15076, "payload size mismatch"
    assert hashlib.sha256(blob).hexdigest()==EXPECTED_PAYLOAD_SHA256, "payload digest mismatch"
    raw=lzma.decompress(blob,format=lzma.FORMAT_XZ)
    assert len(raw)<120000, "oversized decompressed payload"
    offset=0
    result={}
    while offset<len(raw):
        nul=raw.index(b"\x00",offset)
        end=raw.index(b"\n",nul+1)
        name=raw[offset:nul].decode("ascii")
        length=int(raw[nul+1:end].decode("ascii"))
        assert name in EXPECTED and name not in result and 0<length<20000,"unsupported source entry"
        payload=raw[end+1:end+1+length]
        assert len(payload)==length,"truncated payload"
        assert hashlib.sha256(payload).hexdigest()==EXPECTED[name],"source SHA mismatch: "+name
        result[name]=payload
        offset=end+1+length
    assert set(result)==set(EXPECTED), "missing or extra files"
    dest=HERE/"native";dest.mkdir(exist_ok=True)
    for name,src in result.items():
        path=dest/name
        assert not path.exists(),"refuse to overwrite existing file "+name
        path.write_bytes(src)
    print(json.dumps({"status":"B38_ORIGINAL_SOURCES_BYTE_IDENTICAL","source_files":len(result),
                      "payload_sha256":EXPECTED_PAYLOAD_SHA256,"sources_sha256":EXPECTED},sort_keys=True))
if __name__=="__main__":main()
