# MoveOps

A CLI for managing the address-change cascade after a move, because "update
your address everywhere" is actually forty small tasks with different
deadlines, and something always gets missed.

Seed a checklist from a template, track status per item (with confirmation
numbers and completion dates), see what's overdue or coming up next, and
export a printable one-pager.

## Install

```bash
pip install -e .
```

## Usage

```bash
# Seed a new checklist
moveops init --template wisconsin --move-date 2026-08-01 \
  --from "Fond du Lac, WI" --to "DeForest, WI"

# See what's overdue or due soon, sorted by urgency
moveops status

# List everything, optionally filtered
moveops list --category "Time-sensitive"
moveops list --status pending

# Mark an item done
moveops complete id-license --confirmation ABC123

# Export a printable Markdown one-pager
moveops export --output move-checklist.md
```

State lives in `moveops_state.json` in the current directory by default
(override with `--state-file`).

## Templates

- `generic`: baseline checklist for any move.
- `wisconsin`: overlays WI-specific deadlines (DMV: 30 days, USPS forwarding,
  voter registration, National Guard admin records) on top of `generic`.

Templates are YAML files under `src/moveops/templates/`. A template can
`extends:` another template and override individual items by `id`. The
override replaces that item's category/title/deadline/notes wholesale, so an
item can move between categories (e.g. Wisconsin promotes the generic
"driver's license" item into "Time-sensitive" with a 30-day deadline). New
state templates (for other states/countries) are welcome via PR: copy
`generic.yaml`'s structure or `extends: generic` and override what differs.

## Development

```bash
pip install -e ".[dev]"
pytest
```
