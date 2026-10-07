# COSMIC-TRACE

Explainable AI for Discovering and Understanding Change in the Infrared Sky.

## Prototype focus

This repository now includes a working demo prototype for the NASA SPHEREx-inspired discovery story:

- a sky explorer view
- a Sky Time Machine timeline
- a candidate object that changes across epochs
- AI anomaly explanation
- a scientific discovery passport summary

## Run locally

```bash
cd /path/to/COSMIC-TRACE
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Then visit:

http://localhost:8000/

## Project story

The demo follows the core narrative:

1. Open the sky explorer.
2. Watch the observation epochs evolve in the time machine.
3. Select a candidate object.
4. Reveal motion, brightness, and spectral changes.
5. Explain why the source is scientifically interesting.
6. Present the discovery passport.

## Notes

This is intentionally a compact prototype based on synthetic SPHEREx-like data so the full science story can be demonstrated without needing a full mission dataset in the first pass.
