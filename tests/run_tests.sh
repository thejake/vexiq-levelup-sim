#!/bin/zsh
# Headless regression tests for the simulator. Run from the repo root:
#   ./tests/run_tests.sh
set -e
cd "$(dirname "$0")/.."
out=$(mktemp -d)

echo "== api smoke =="
uv run python -m vexsim tests/api_smoke.py --headless --max-sim-seconds 30 | grep "ALL PASS"

echo "== square closes =="
uv run python -m vexsim examples/first_drive.py --headless --max-sim-seconds 30 \
    --dump-state "$out/sq.json" > /dev/null
python3 - "$out/sq.json" <<'EOF'
import json, sys
p = json.load(open(sys.argv[1]))["pose"]
dx, dy = abs(p["x"] - 48.5), abs(p["y"] - 9.0)
dh = min(p["heading_cw"], 360 - p["heading_cw"])
assert dx < 1.5 and dy < 1.5 and dh < 4, p
print(f"ok: x off {dx:.2f}in, y off {dy:.2f}in, heading off {dh:.2f} deg")
EOF

echo "== preload scores =="
uv run python -m vexsim examples/score_preload.py --headless --max-sim-seconds 40 \
    --dump-state "$out/sc.json" > /dev/null
python3 - "$out/sc.json" <<'EOF'
import json, sys
s = json.load(open(sys.argv[1]))
assert s["score"]["red"] == 1, s["score"]
print("ok: red goal = 1")
EOF

echo "== pyramid mechanics: preload reaches L3 (12 pts) =="
uv run python -m vexsim examples/pyramid_place.py --headless --max-sim-seconds 35 \
    --dump-state "$out/pyr.json" > /dev/null
python3 -c "
import json, sys
s = json.load(open('$out/pyr.json'))
assert s['score']['red'] == 12, s['score']
print('ok: red pyramid L3 = 12 pts')
"

echo "ALL TESTS PASS"
