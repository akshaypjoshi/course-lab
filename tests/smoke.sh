#!/usr/bin/env bash
# Smoke test: build course-studio's example DSA course with course-lab's example quiz, take the quiz
# headless on desktop and phone + dark, build a standalone retest page, and confirm bad quizzes fail.
#   tests/smoke.sh
# Uses course-studio from COURSE_STUDIO=<path to skills/course-studio>, or clones akshaypjoshi/course-studio.
# Needs: python deps from skills/course-lab/requirements.txt, Chromium for Playwright, Node 20.10+.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$ROOT/skills/course-lab"
PY="${PYTHON:-python3}"
WS="$(mktemp -d)"
trap 'rm -rf "$WS"' EXIT

if [ -z "${COURSE_STUDIO:-}" ]; then
  git clone --quiet --depth 1 https://github.com/akshaypjoshi/course-studio "$WS/course-studio"
  export COURSE_STUDIO="$WS/course-studio/skills/course-studio"
fi
echo "course-studio: $COURSE_STUDIO"

# the example course from course-studio, with course-lab's quiz added to its Hashing chapter
mkdir "$WS/courses"
cp -R "$COURSE_STUDIO/examples/courses/dsa" "$WS/courses/dsa"
cp "$SKILL/examples/courses/dsa/chapters/05-hashing/quiz.json" "$WS/courses/dsa/chapters/05-hashing/quiz.json"
"$PY" "$COURSE_STUDIO/scripts/workspace.py" init "$WS/courses"
for fig in "$WS"/courses/dsa/chapters/*/figures/*/; do
  (cd "$fig" && node build.mjs)
done

"$PY" "$SKILL/scripts/lab.py" build "$WS/courses/dsa" --catalog
"$PY" "$SKILL/scripts/lab.py" validate "$WS/courses/dsa/chapters/05-hashing/quiz.json" --course-dir "$WS/courses/dsa" | tee "$WS/validate.txt"
test "$(tail -1 "$WS/validate.txt")" = "ok"
grep -q 'data-quiz=' "$WS/courses/dsa/dist/05-hashing.html"
grep -q 'href="#quiz">Test yourself' "$WS/courses/dsa/dist/05-hashing.html"

# rebuilding never injects a quiz twice
"$PY" "$SKILL/scripts/lab.py" build "$WS/courses/dsa" > /dev/null
test "$(grep -o '<section class="lab" id=' "$WS/courses/dsa/dist/05-hashing.html" | wc -l | tr -d ' ')" = "1"

# a standalone retest page (questions reordered, chapter set at the top level)
mkdir -p "$WS/courses/dsa/retests"
"$PY" - "$SKILL/examples/courses/dsa/chapters/05-hashing/quiz.json" "$WS/courses/dsa/retests/dsa-05-hashing-retest-1.json" <<'PY'
import json, sys
q = json.load(open(sys.argv[1]))
q.update(title="Hashing, retest 1", id="dsa-05-hashing-retest-1", chapter=5)
qs = q["questions"]
q["questions"] = qs[1:3] + qs[:1] + qs[4:7] + qs[3:4] + qs[8:] + qs[7:8]
json.dump(q, open(sys.argv[2], "w"))
PY
"$PY" "$SKILL/scripts/lab.py" quiz "$WS/courses/dsa/retests/dsa-05-hashing-retest-1.json" "$WS/courses/dsa"
test -f "$WS/courses/dsa/dist/dsa-05-hashing-retest-1.html"

# take every quiz: all right, all wrong, mixed with a guess and a blank; desktop, then phone + dark
"$PY" "$SKILL/scripts/check_lab.py" "$WS/courses/dsa/dist" --all

# bad quizzes are caught
"$PY" - "$SKILL/examples/courses/dsa/chapters/05-hashing/quiz.json" "$WS/bad/quiz.json" <<'PY'
import json, os, sys
q = json.load(open(sys.argv[1]))
for x in q["questions"]:
    x["answer"] = 0
q["questions"][0]["difficulty"] = "trivial"
del q["questions"][1]["section"]
os.makedirs(os.path.dirname(sys.argv[2]), exist_ok=True)
json.dump(q, open(sys.argv[2], "w"))
PY
OUT="$("$PY" "$SKILL/scripts/lab.py" validate "$WS/bad/quiz.json" || true)"  # exits 1, as intended
grep -q "difficulty must be easy/medium/hard" <<<"$OUT" || { echo "validate missed a bad difficulty"; exit 1; }
grep -q "missing 'section'" <<<"$OUT" || { echo "validate missed a missing section"; exit 1; }
grep -q "answer skew" <<<"$OUT" || { echo "validate missed answer skew"; exit 1; }

echo "smoke test passed"
