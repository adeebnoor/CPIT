# Lecture design requirements · data and checks

Source: the instructor's report **"متطلبات تصميم المحاضرات — مقرر CPIT"** (14 October 2026). It lists 37 requirements
in six groups (KEEP, COV, LANG, CASE, TIME, RUB). Each one is either **must** (blocks a release), **pref**
(preferred; a warning) or **manual** (reviewed by the instructor and recorded in the status table).

## Files

| File | What it holds |
|---|---|
| `common.json` | Course-level settings: lecture length (50 min), core budget share (85%), the time rule, the forbidden argument-framework terms, the rubric template. |
| `chNN.json` | The authored requirement data for one lecture: case tags, glossary (with Arabic), transfer case, per-slide minutes/tier/concept/answer element/common error/source lists, station rubrics, quiz tags, activities, coverage map and study list. |
| `../../tools/apply_lecture_requirements.py` | Writes the authored data into the pinned `lecture-data` block of each lecture and the rubric examples block of each assignment page (Ch12 onwards). |
| `../../tools/check_lecture_requirements.py` | Checks every requirement that can be checked by machine and writes `docs/lecture-requirements-status.md`. `build_public_site.py` runs it and refuses to stage when a **must** item fails. |
| `../../tools/lecture_requirements_lib.py` | Shared readers: lecture data, source ledgers, story strings, the student-text extractor used by the language checks. |

## Workflow after a content change

```
python3 tools/apply_lecture_requirements.py 12        # or no argument for all nine lectures
python3 tools/check_lecture_requirements.py           # prints FAIL/WARN lines and rewrites the status table
python3 tools/prepare_readable_release.py && python3 tools/refresh_release_hashes.py --revision <id> --note "..."
python3 tools/build_public_site.py
```

The status table is the acceptance list: `docs/lecture-requirements-status.md`.

## Data model (per lecture)

- **Lecture level**: `lectureMinutes`, `budgetShare`, `timeRule`, `glossary[{term, short, ar, added}]`,
  `transfer{title, text, source|fictional, question, answer, concept, answerKey, at}`,
  `coverage[{n, title, cls: slide|full|no, unit, reason, kind: list|table|figure|prose|title, items}]`,
  `studyList[{topic, sources[], book{page,label}, note}]`, `activities[{id, label, at, minutes, tier}]`,
  `case.fictional`, `case.answerKey`.
- **Slide level**: `minutes`, `tier` (core|optional), `concept`, `answerKey`, `concept2`/`answerKey2` with
  `question2`/`answer2`, `commonError` (instructor notes), `lists[{source, title, items}]` (source lists shown
  in full), `added` (course addition), `twist` (the assumption-change slide), `transfer` (carries the transfer
  case), `sourceFigs[]` (figures linked to the source ledger).
- **Station level**: `minutes`, `tier`, `concept`, `answerKey`, `rubric{criteria[{name, levels[[marks,label,text]]}], marks, strong{text,why}, weak{text,why}, other}`.
- **Quiz level**: `concept`, `answerKey`, `beyondCase`.

## Decisions recorded for the preferred items

- KEEP-8, COV-6, LANG-5, LANG-6, TIME-5, TIME-6 and RUB-6 are implemented (see the status table).
- Assignments 1–2 (Ch10, Ch11) keep their original pages; rubric examples are written from Assignment 3 (Ch12) onwards (`assignmentRubricFromChapter`).
- The lecture duration is a course-level setting (`lectureMinutes` in `common.json`, copied to `publication.json`).
