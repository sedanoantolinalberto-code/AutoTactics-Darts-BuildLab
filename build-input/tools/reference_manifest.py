"""Generate/validate a SHA256 manifest of this supplement without executing media."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'MANIFEST_SHA256.json'
EXCLUDE = {'MANIFEST_SHA256.json'}

def members():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name not in EXCLUDE
                  and '__pycache__' not in p.parts and p.suffix not in {'.pyc', '.exe', '.o', '.obj'})

def create():
    return {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in members()}

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('write', 'verify'):
        raise SystemExit('usage: python tools/reference_manifest.py write|verify')
    if sys.argv[1] == 'write':
        MANIFEST.write_text(json.dumps({'schema':'s34-v19-sha256','files':create()},indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print('manifest created')
        return
    expected = json.loads(MANIFEST.read_text(encoding='utf-8'))['files']
    current = create()
    if expected != current:
        missing = sorted(set(expected)-set(current))
        extra = sorted(set(current)-set(expected))
        changed = sorted(k for k in set(current)&set(expected) if current[k] != expected[k])
        raise SystemExit(f'FAIL missing={missing} extra={extra} changed={changed}')
    print(f'PASS SHA256 manifest {len(current)}/{len(current)}')

if __name__=='__main__':
    main()
