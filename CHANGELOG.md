# Changelog

## 0.1.0 (2026-10-14)

First release.

- **Chapter quizzes.** Every Course Studio chapter can end with a 10-question "Test yourself" section (3 easy, 4 medium, 3 hard), added to the page and its table of contents by `lab.py build`.
- **Instant grading in the page**: weighted score (1/2/3 points), level (Mastered, Proficient, Developing, Needs review), breakdowns by difficulty and topic, Revisit links to the sections, confident mistakes vs guesses, explanations and the picked option's rationale, retake, and the last 10 attempts kept in the browser. Light, dark and phone.
- **Copy results for Claude**: a stable line-based report that the skill evaluates (misconception, gap, shaky, slip) into a short reply and a targeted 10-question retest page (`lab.py quiz`).
- **Final tests** across the written chapters, at the end of the course page, grouped by chapter.
- `lab.py validate` checks structure, the mix, answer-position skew, topic spread and that every section resolves; `check_lab.py` takes every quiz headless (all right, all wrong, mixed with a guess and a blank) on desktop and phone + dark.
- Finds Course Studio in project or home skill folders, Claude Code plugin installs, `/mnt/skills`, or `COURSE_STUDIO`.
- No em dashes anywhere, including the in-page quiz text and the results report, so built pages pass Course Studio's page check.
- Example: a verified quiz for Course Studio's Hashing chapter.
- Website at [skills.akshayjoshi.dev/course-lab](https://skills.akshayjoshi.dev/course-lab/) with the quiz running live.
