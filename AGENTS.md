# Repository Guidelines

## Project Structure & Module Organization

This repository stores course materials for web development labs. The root
`readme.md` contains the main course overview and lab descriptions in Russian.
Published documentation lives under `docs/`: `docs/index.md` is the entry page,
and lab-specific pages are grouped as `docs/lr1/`, `docs/lr2/`, `docs/lr3/`,
etc. Student work belongs under `students/`, currently organized by group, for
example `students/k3339/`. IDE metadata such as `.idea/` is not part of the
content model and should not be edited for documentation changes.

## Build, Test, and Development Commands

There is no application build pipeline in this repository. Treat changes as
Markdown documentation updates unless a student submission adds its own tooling.

- `git status`: review local changes before editing or committing.
- `find . -maxdepth 3 -type f ! -path './.git/*'`: inspect tracked content when
  ripgrep is unavailable.
- `python3 -m http.server 8000 -d docs`: preview `docs/` locally at
  `http://localhost:8000/` if rendered Markdown output is needed.

If a subdirectory introduces a `package.json`, `pyproject.toml`, `Makefile`, or
Docker files, run commands from that subdirectory and document them there.

## Coding Style & Naming Conventions

Use Markdown for course documentation. Keep headings descriptive, sentence case
or title case, and avoid skipping heading levels. Prefer relative links for
internal pages, for example `../lr2/` or `./lr1/`. Preserve Russian terminology
and course wording unless intentionally correcting typos or updating policy.
Name lab folders with the existing `lrN` pattern and place each page in an
`index.md` file.

## Testing Guidelines

For documentation-only changes, verify links and basic rendering manually. Check
that new internal links resolve from the generated `docs/` structure and that
tables, code fences, and numbered lists render correctly. Student code should
include its own test instructions inside the relevant submission directory when
applicable.

## Commit & Pull Request Guidelines

Recent history uses short commit subjects such as `Z2` and descriptive subjects
like `Add lab report and GitHub Pages docs`. Prefer a clear imperative summary,
for example `Update lab 3 Docker instructions`. Pull requests should describe
the changed lab or document, mention affected paths, link related issues or
course tasks, and include screenshots when page rendering changes.

## Agent-Specific Instructions

Do not rewrite or reorganize student submissions unless explicitly asked.
Keep documentation edits narrow, preserve existing language, and avoid changing
course deadlines or grading rules without a clear source in the request.
