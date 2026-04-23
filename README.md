# PRISM — Zero-Trust Hybrid Email Scoring Engine

PRISM is a compact research/demo pipeline for scoring incoming emails using a hybrid "zero-trust" approach. It combines linguistic (semantic/NLP) analysis with metadata/forensic heuristics and a decision math engine (DTS) to produce allow/challenge/block recommendations.

This README explains how to set up the project, run the pipeline and UI, generate datasets, and troubleshoot the most common environment issues (including the PyTorch / NumPy mismatch you encountered).

## Highlights

- Linguistics (Track A): zero-shot or model-backed semantic scoring (`Main/linguistics.py`).
- Behaviour/Identity (Track B): metadata and behavioral heuristics (`Main/behaviourIdentity.py`).
- Decision math engine (DTS): fuses signals into final decisions (`Main/dts.py`).
- Dataset helpers to generate synthetic emails using OpenAI or Google Gemini (API keys required): `Dataset/generate-emails_openai.py`, `Dataset/generate-emails_gemini.py`.
- Streamlit UI for quick exploration: `app.py`.

## Repository structure

- `app.py` — Streamlit dashboard that runs the pipeline interactively.
- `requirements.txt` — main Python dependency pins (see notes about NumPy / PyTorch below).
- `Dataset/` — helpers and sample CSVs; utilities to compile datasets (`compile-dataset.py`).
- `Main/` — core pipeline code and small unit tests:
  - `ingest.py` — EML parsing / payload construction
  - `linguistics.py` — semantic/linguistic scoring (uses Hugging Face transformers if available)
  - `behaviourIdentity.py` — metadata and forensic heuristics
  - `dts.py` — decision math and scoring fusion
  - `determine-accuracy.py` — evaluation utilities (note: currently flawed and being worked on — see Development notes)
  - tests: `test-ingest.py`, `test-behaviourIdentity.py`, `test-linguistics.py`

## Quick start (recommended: venv)

1) Create and activate a virtual environment (replace `<env>` with your chosen env directory):

```bash
python3.11 -m venv <env>
# macOS / Linux
source <env>/bin/activate
# Windows (PowerShell)
<env>\Scripts\Activate.ps1
```

2) Install dependencies (note: the repo's `requirements.txt` already pins `numpy<2` to avoid runtime ABI issues with some prebuilt PyTorch wheels):

```bash
python3.11 -m pip install --upgrade pip
python3.11 -m pip install -r requirements.txt
```

3) Run the pipeline on a sample email (CLI):

```bash
python3.11 Main/main.py  # uses Dataset samples by default
```

4) Start the Streamlit UI (optional):

```bash
streamlit run app.py
```

## Optional: conda/mamba (not required — venv is sufficient)

For most development and testing in this repository, a standard Python `venv` is sufficient and recommended. Conda/mamba is optional and only useful in some cases where a prebuilt PyTorch wheel for your platform is unavailable via pip (for example, certain Apple Silicon configurations). If you run into a platform-specific PyTorch wheel problem, conda can help.

Example conda steps (only if needed):

```bash
# create env
conda create -n prism python=3.11 -y
conda activate prism

# install PyTorch (pick the correct channel for your hardware)
conda install -c pytorch -c conda-forge pytorch torchvision torchaudio -y

# then install the repo Python deps
python -m pip install -r requirements.txt
```

Using conda often resolves the "torch wheel not available for macOS" problem and provides a prebuilt binary compatible with your system.

## Running tests

The `Main/` folder contains small unit tests. Run them with pytest:

```bash
# from repo root, with virtual environment (venv/conda) active
python3.11 -m pip install pytest
pytest -q
```

## Dataset generation

- The `Dataset/generate-emails_openai.py` and `Dataset/generate-emails_gemini.py` scripts show how to synthesize labeled emails using the respective APIs. They require API keys and network access.
- Recommendation: prefer the OpenAI-based generator (`generate-emails_openai.py`) when possible — it has been found more reliable in practice than the Gemini-based generator. Use Gemini only if you require Gemini-specific data or have a stable Gemini setup.
- Use `Dataset/compile-dataset.py` to combine generated CSV pieces into a single dataset for training/evaluation. Check the top of each script for usage examples.

## Key entry points and functions
- `Main/main.py` — top-level runner that wires ingestion, analysis, and DTS for a single file or directory.
- `Main/ingest.parse_eml_to_payload` — turns `.eml` into the pipeline payload (subject, body, headers, attachments).
- `Main/linguistics.analyze_linguistics` — performs zero-shot or model-backed linguistic scoring (returns a legitimacy score).
- `Main/behaviourIdentity.analyze_metadata` — extracts metadata signals used by DTS.
- `Main/dts.evaluate_transaction` — fuses signals into a final decision and suggested action.

## Troubleshooting — PyTorch / NumPy / Transformers issues

You already saw a concrete issue: startup printed messages like "PyTorch was not found..." and later `NameError: name 'classifier' is not defined`. That happens when `transformers` detects PyTorch is unavailable (or incompatible) and the code that creates the pipeline didn't run.

Common root causes and remedies:

- NumPy ABI mismatch (very common): If you have `numpy` 2.x but a prebuilt extension (like some torch wheels) was compiled against NumPy 1.x, imports fail. The quickest fix is to install a 1.x NumPy in the same environment:

```bash
python3.11 -m pip install --upgrade --force-reinstall "numpy<2"
```

- PyTorch wheel not available for your macOS/Python combination: pip may not find `torch>=2.4` for your platform (common on Apple Silicon or older macOS). Two options:
  1. Use conda/mamba to install a compatible `pytorch` package from the `pytorch` and `conda-forge` channels (only needed in some edge cases).
  2. If you must stay with pip and the available torch is older (e.g., 2.2.2), pin `transformers` to a version compatible with that torch release (not ideal).

- After making environment changes, verify imports:

```bash
python3.11 -c "import numpy, torch; print('numpy', numpy.__version__, 'torch', getattr(torch, '__version__', None))"
python3.11 -c "from transformers import pipeline; pipeline('zero-shot-classification', model='roberta-large-mnli') and print('pipeline OK')"
```

If `pipeline(...)` fails with a message about missing `torch` or `torch` being disabled, either PyTorch is not installed correctly, or `transformers` was installed with an expectation of a newer torch than available.

If you prefer not to install PyTorch (or want a faster startup for testing), the code has a heuristic fallback: linguistic scoring will run a lightweight keyword-based check when the transformer pipeline isn't available. That avoids the NameError but gives a weaker signal.

## Development notes and recommended small fixes

- Defensive initialization: the `linguistics` module should create a module-level `classifier = None` and handle the case when pipeline creation fails; otherwise callers get `NameError` when they assume `classifier` exists. (A simple fallback heuristic avoids crashing when transformers/pytorch are unavailable.)
- `Main/determine-accuracy.py` status: the `determine-accuracy.py` program is known to be flawed and is actively being worked on — avoid relying on its current output for production decisions. Fixes are in progress and will be documented in the repo when ready.
- Use a consistent environment strategy: maintain a virtual environment and pin `numpy<2` (fast, recommended). Conda is optional and only needed if you hit a platform-specific PyTorch wheel problem.

## Example: reproduce the issue and verify the fix

1. Activate your virtual environment and downgrade numpy if needed:

```bash
# Replace <env> with the directory of your virtual environment
source <env>/bin/activate
python3.11 -m pip install --upgrade --force-reinstall "numpy<2"
```

2. Verify torch and transformers imports succeed (or install via conda if pip cannot provide a matching torch):

```bash
python3.11 -c "import torch; print('torch', torch.__version__)"
python3.11 -c "python - <<'PY'
from transformers import pipeline
pipeline('zero-shot-classification', model='roberta-large-mnli')
print('pipeline OK')
PY"
```

3. Run the main pipeline sample:

```bash
python3.11 Main/main.py
```

If you still see: `Warning: Could not load RoBERTa model. Error: name 'torch' is not defined` — it means at runtime the `transformers` import or pipeline call raised an exception (or `torch` was not visible). Re-check the environment used to run Python: the active virtualenv must be the one with torch installed.

## Contributing

- Open issues for bugs or features.
- Tests live in `Main/` and can be run with `pytest`.
