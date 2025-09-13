# AMEEL — AI Assistant for E‑commerce & Accounting

**Project name:** AMEEL
**Creator:** Mohammad from India — graphic designer, software developer, social media manager, and coach in makeup academy.

## What this repo contains (prototype)
- `backend/` — FastAPI-based API skeleton for core AI endpoints (chat, stt, tts, image-gen, analyze-image).
- `frontend/` — Streamlit prototype UI (Jarvis-style voice + chat + simple dashboard).
- `utils/` — placeholder helpers for OpenRouter/OpenAI integrations, OCR, and bookkeeping utilities.
- `assets/` — placeholder logo, sample files.
- `README.md` — this file.
- `requirements.txt` — Python dependencies (prototype).
- `LICENSE` — MIT

> This is a prototype scaffold. You must add your API keys (OpenRouter/OpenAI/ElevenLabs/etc.) to `backend/.env` or environment variables before running.

## Quick start (prototype)
1. Create a Python virtualenv and activate it.
2. `pip install -r requirements.txt`
3. Run backend:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
4. Run frontend (in separate terminal):
   ```bash
   streamlit run frontend/app.py
   ```

## Notes
- Endpoints and wrappers include clear `TODO` markers where you must insert API calls and keys.
- Arabic voice: configure your preferred STT/TTS provider in `utils/openrouter_client.py` or environment variables.
- Image generation: uses an abstracted `generate_image()` function — replace with Stable Diffusion / OpenAI Image API calls.

---
Project created for Duaa (friend) by Mohammad.
