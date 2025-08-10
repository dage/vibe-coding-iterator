from __future__ import annotations
import json, time, sys, requests, glob

BASE = "http://localhost:8000"


def sse_first(url: str, timeout: int = 5):
    t0 = time.time()
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data: "):
                return json.loads(line[6:])
            if time.time() - t0 > timeout:
                raise TimeoutError("no SSE")


def main() -> int:
    # index reachable
    r = requests.get(BASE + "/", timeout=5)
    assert r.status_code == 200
    # wait for one event
    ev = sse_first(BASE + "/api/events")
    assert "t" in ev
    # allow an iteration to run
    time.sleep(3)
    shots = glob.glob("storage/runs/*/screenshots/snap_*.png")
    assert shots, "no screenshots found"
    print("SMOKE OK")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("SMOKE FAIL:", e)
        sys.exit(1)


