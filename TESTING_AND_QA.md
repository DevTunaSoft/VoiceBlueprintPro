# Testing and QA

## Commands
- Backend focused: `uv run python -m pytest -q tests/test_project_bundle.py`
- Mobile contract: `uv run python -m pytest -q tests/test_mobile_contract.py`
- Locale parity: `uv run python -m pytest -q tests/test_locale_parity.py`
- Changelog style: `uv run python -m pytest -q tests/test_changelog_style.py tests/test_changelog_fragments.py`
- Structure doc: `uv run python -m pytest -q tests/test_structure_doc.py`
- Identity gate: `uv run python -m pytest -q tests/test_identity_gate.py`

## Notes
- Tests may require uv environment for torch/uvicorn/cryptography.
- Windows default encoding can cause test read failures; use UTF-8.
- Do not claim full CI green without Actions evidence.
