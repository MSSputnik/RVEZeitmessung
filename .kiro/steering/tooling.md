# Tooling conventions

This project is managed with [uv](https://docs.astral.sh/uv/). Always use `uv`
to run Python and project tools so the project's virtual environment and locked
dependencies are used.

## Running Python

- Run Python programs with `uv run`, never with a bare `python`/`python3`.
  - Run a script: `uv run main.py`
  - Run a module: `uv run python -m <module>`
  - Example: `uv run convert.py --event-report samples/events.csv --wait-report samples/wait.csv --jira-import samples/jira_import.csv`

## Running tests

- Run the test suite with `uv run python -m pytest`, not a bare `pytest`.
  - Full suite: `uv run python -m pytest`
  - A single file: `uv run python -m pytest tests/test_convert.py`

## Running ruff

- Run ruff with `uv run ruff`, never with a bare `ruff`.
  - Lint: `uv run ruff check .`
  - Organize imports: `uv run ruff check --select I --fix .`
  - Format: `uv run ruff format .`

## Writing Markdown

- Write Markdown tables in the compact (non-padded) GitHub Flavored Markdown
  style: each cell is only as wide as its text, and the delimiter row is a
  minimal `| --- | --- |`. Do **not** pad cells with spaces to align columns,
  because the extra padding trips up the Markdown linter. Both styles render
  identically, so always prefer the compact one.
- Example:

  ```markdown
  | Argument | Description |
  | --- | --- |
  | `--file` | Input JSON file. Must exist. |
  | `--sort` | Optional flag. Off by default. |
  ```

- Follow common `markdownlint` rules so generated Markdown stays lint-clean.
  Before finishing any work that creates or edits a Markdown file, review the
  file and fix lint issues automatically rather than leaving them for the user.
  The most common ones to check:
  - **MD032 (blanks-around-lists):** surround every list with a blank line
    before the first item and after the last item.
  - **MD031 (blanks-around-fences):** surround fenced code blocks with blank
    lines.
  - **MD022 (blanks-around-headings):** put a blank line above and below every
    heading.
  - **MD040 (fenced-code-language):** give every fenced code block a language
    (for example ```` ```text ````).
  - **MD047 (single-trailing-newline):** end the file with exactly one newline.
  - **MD009 (no-trailing-spaces):** do not leave trailing whitespace on a line.
