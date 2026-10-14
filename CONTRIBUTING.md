# Contributing

Issues and pull requests are welcome.

## Before you open a PR

1. Install the dependencies: `pip install -r skills/course-lab/requirements.txt && python3 -m playwright install chromium`. You also need Node.js 20.10+ and git.
2. Run `tests/smoke.sh`. It clones Course Studio (or uses `COURSE_STUDIO=<path to skills/course-studio>`), builds its example DSA course with this repo's Hashing quiz, builds a retest page, takes every quiz headless on desktop and on phone in dark mode, and confirms that `lab.py validate` catches a broken quiz.
3. If you changed how the skill behaves, add or update a case in `evals/` and a line in `CHANGELOG.md`.

## Style

- **No em dashes**, in the skill's instructions, in quizzes, or in anything the page shows (including `quiz.js` strings and the results report). Use a comma, a colon, parentheses or a new sentence. En dashes in number ranges (`1–3`) are fine. Course Studio's page check flags em dashes on built pages, and CI fails on any em dash in the repository; run `tools/check_no_em_dash.py` to check locally.
- Keep `SKILL.md` short and move the details into `references/`.
- Scripts use only the packages in `requirements.txt` and must run on Python 3.9. `quiz.js` is plain ES5 with no dependencies, so built pages stay self-contained.
- The results report is a contract: Claude's evaluation and any platform that stores results parse its `Q<n> [difficulty · topic] picked X: correct|wrong` lines. Change it only with a matching change to `references/evaluation.md` and a CHANGELOG entry.

## Course Studio

Course Lab only writes and grades quizzes; pages come from [Course Studio](https://github.com/akshaypjoshi/course-studio). `lab.py` injects into the HTML that Course Studio's `build_course.py` produces (numbered `<h2 id=...><span class="num">` headings, `nav.toc`, `nav.pager`), so a change to that markup there needs a matching change here. The smoke test runs against Course Studio's current `main`.

## Releases

Bump `version` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, add a `CHANGELOG.md` entry, and tag the commit `vX.Y.Z`.
