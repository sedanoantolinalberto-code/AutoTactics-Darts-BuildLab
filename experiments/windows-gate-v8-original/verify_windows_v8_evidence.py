"""B25 review-only verifier of a claimed Windows V8 result.

Checks shape, internal consistency, expected cases, and source hashes. This is
NOT an attestation of environment identity or independent native execution.
"""
from __future__ import annotations
import datetime, hashlib, json, math, pathlib, re, unittest
import windows_gate_v8 as gate

class RejectedEvidence(ValueError):pass

EXPECTED_FILES=tuple(gate.SOURCES)
EXPECTED_TESTS=tuple('windows_gate_v8.WindowsGateV8.'+n for n in
                     sorted(n for n in dir(gate.WindowsGateV8) if n.startswith('test_')))
assert len(EXPECTED_TESTS)==17


def verify_report(data:dict, source_dir:pathlib.Path)->dict:
    def require(condition, message):
        if not condition: raise RejectedEvidence(message)
    require(type(data) is dict,'invalid report object')
    require(data.get('schema')=='engineyt-windows-gate-v8-b23-reviewonly','wrong schema')
    require(data.get('pass') is True,'not a passing result')
    require(isinstance(data.get('os'),str) and data['os'].startswith('Windows-'),'not a Windows report')
    require(data.get('test_filesystem')=='NTFS','native filesystem not NTFS')
    for key,value in [('total',17),('passed',17),('failures',0),('errors',0),('skipped',0)]:
        require(type(data.get(key)) is int and data[key]==value,'count mismatch: '+key)
    reported_cases=data.get('cases')
    require(type(reported_cases) is list and len(reported_cases)==17,'wrong case count')
    names=[]
    for case in reported_cases:
        require(type(case) is dict,'bad case')
        require(case.get('status')=='PASS','case not passed')
        name=case.get('test')
        require(type(name) is str and name,'missing test name')
        duration=case.get('elapsed_s')
        require(type(duration) in (int,float) and math.isfinite(duration) and duration>=0,'bad duration')
        names.append(name)
    require(sorted(names)==sorted(EXPECTED_TESTS),'missing, duplicated or unexpected tests')
    hashes=data.get('source_hashes_sha256')
    require(type(hashes) is dict and set(hashes)==set(EXPECTED_FILES),'source-list mismatch')
    for name in EXPECTED_FILES:
        claim=hashes[name]
        require(type(claim) is str and bool(re.fullmatch('[0-9a-f]{64}',claim)), 'bad source digest')
        p=pathlib.Path(source_dir)/name
        require(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==claim,'stale source: '+name)
    stamp=data.get('timestamp_utc')
    require(type(stamp) is str,'missing timestamp')
    try: parsed=datetime.datetime.fromisoformat(stamp)
    except (ValueError,TypeError):raise RejectedEvidence('invalid timestamp') from None
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None,'naive timestamp')
    return {'status':'SELF_REPORTED_WIN_V8_CONSISTENT_NOT_ATTESTED',
            'cases':17,'verified_source_files':len(EXPECTED_FILES),
            'native_execution_independently_attested':False,
            'production_authorized':False}


def main(args=None):
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report',type=pathlib.Path)
    parser.add_argument('--source-dir',type=pathlib.Path,default=pathlib.Path(__file__).parent)
    a=parser.parse_args(args)
    try:
        verdict=verify_report(json.loads(a.report.read_text(encoding='utf8')),a.source_dir)
    except (RejectedEvidence,ValueError,OSError) as exc:
        print(json.dumps({'status':'BLOCKED_OR_INVALID','error_type':type(exc).__name__}))
        return 2
    print(json.dumps(verdict,sort_keys=True));return 0

if __name__=='__main__':raise SystemExit(main())
