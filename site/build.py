#!/usr/bin/env python3
"""Build the Course Lab site: the landing page plus a live demo built by the skill itself.

    python3 site/build.py <out-dir>

Output:
    <out>/index.html, <out>/assets/...             landing page
    <out>/example/dsa/index.html                   course-studio's example DSA course page
    <out>/example/dsa/05-hashing.html              the Hashing chapter, its quiz at the end
    <out>/example/dsa/try-hashing-quiz.html        the same quiz on its own page (embedded on the landing page)

course-studio comes from COURSE_STUDIO=<path to skills/course-studio>, or is cloned from GitHub.
Needs: python deps from skills/course-lab/requirements.txt (playwright not needed), git and Node.js 20.10+.
The hub repo (akshaypjoshi/skills) runs this to publish skills.akshayjoshi.dev/course-lab/.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SKILL = ROOT / "skills" / "course-lab"
ASSETS = ("quiz-light.png", "quiz-dark.png", "result-light.png", "result-dark.png")
CS_REPO = "https://github.com/akshaypjoshi/course-studio"
TOP_LINKS = ("<script>if (window.top !== window) document.addEventListener('click', function (e) {"
             " var a = e.target.closest && e.target.closest('a[href]');"
             " if (a && a.getAttribute('href').charAt(0) !== '#') a.target = '_top'; }, true);</script>")


def run(*cmd, cwd=None, env=None):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], cwd=cwd, check=True, env=env)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1]).resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # landing page and its assets
    shutil.copy2(HERE / "index.html", out / "index.html")
    shutil.copytree(HERE / "assets", out / "assets")
    for name in ASSETS:
        shutil.copy2(ROOT / ".github" / "assets" / name, out / "assets" / name)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cs = os.environ.get("COURSE_STUDIO")
        if not cs:
            run("git", "clone", "--quiet", "--depth", "1", CS_REPO, tmp / "course-studio")
            cs = tmp / "course-studio" / "skills" / "course-studio"
        cs = Path(cs).resolve()
        env = dict(os.environ, COURSE_STUDIO=str(cs))

        # course-studio's example DSA course + course-lab's quiz for its Hashing chapter
        courses = tmp / "courses"
        courses.mkdir()
        shutil.copytree(cs / "examples" / "courses" / "dsa", courses / "dsa")
        quiz = SKILL / "examples" / "courses" / "dsa" / "chapters" / "05-hashing" / "quiz.json"
        shutil.copy2(quiz, courses / "dsa" / "chapters" / "05-hashing" / "quiz.json")
        run(sys.executable, cs / "scripts" / "workspace.py", "init", courses, env=env)
        for build in sorted(courses.glob("dsa/chapters/*/figures/*/build.mjs")):
            run("node", "build.mjs", cwd=build.parent)
        run(sys.executable, SKILL / "scripts" / "lab.py", "build", courses / "dsa", env=env)

        # the same quiz as a standalone page, for the live embed
        q = json.loads(quiz.read_text(encoding="utf-8"))
        q.update(id="try-hashing-quiz", chapter=5, heading="Hashing, chapter test")
        standalone = tmp / "try-hashing-quiz.json"
        standalone.write_text(json.dumps(q, ensure_ascii=False), encoding="utf-8")
        run(sys.executable, SKILL / "scripts" / "lab.py", "quiz", standalone, courses / "dsa", env=env)

        # embedded on the landing page: links to other pages open in the main window, not the frame
        page = courses / "dsa" / "dist" / "try-hashing-quiz.html"
        page.write_text(page.read_text(encoding="utf-8").replace("</body>", TOP_LINKS + "</body>", 1), encoding="utf-8")

        shutil.copytree(courses / "dsa" / "dist", out / "example" / "dsa", ignore=shutil.ignore_patterns("shots*"))
    print(f"site built in {out}")


if __name__ == "__main__":
    main()
