# SalinWika Frontend Guide

## What we are building

SalinWika is a Cebuano-to-Tagalog translation project. The repository's main
application is a Python command-line tool that uses Meta's NLLB model for
translation, fine-tuning, and language adaptation.

The `frontend/` directory is a separate SvelteKit web interface. Its purpose is
to give people a simple browser-based way to try the translation experience.

At the moment, the frontend is a **local demo**, not a browser client for the
NLLB Python pipeline. It uses a small set of Cebuano/Tagalog examples defined
inside the frontend code. This is intentional: it keeps the interface usable
without downloading a large model or running a backend server.

## What the demo does

1. Shows a small list of Cebuano corpus examples.
2. Lets a user select one example or type it into the source field.
3. Lets the user choose a local demo model label.
4. Returns the matching Tagalog translation for a supported corpus example.
5. Clearly explains when typed text is outside the demo corpus instead of
   inventing a translation.

For example:

| Cebuano input | Tagalog result |
| --- | --- |
| `Maayong buntag.` | `Magandang umaga.` |
| `Asa ka paingon?` | `Saan ka pupunta?` |

## Run the frontend

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

Vite will print a local URL, normally `http://localhost:5173/`. Open that URL
in a browser.

To create a production build and check that it compiles:

```bash
cd frontend
npm run build
```

## Frontend file map

| File | Responsibility |
| --- | --- |
| `frontend/src/routes/+page.svelte` | Main page state, loading the demo models/examples, and coordinating translation. |
| `frontend/src/lib/api.js` | Local demo data and translation lookup. This is where a real backend request will eventually replace the demo lookup. |
| `frontend/src/lib/components/TranslateBox.svelte` | Cebuano input form and submit button. |
| `frontend/src/lib/components/ResultCard.svelte` | Tagalog result, loading state, and error message. |
| `frontend/src/lib/components/ModelPicker.svelte` | Model selection control and model metadata. |
| `frontend/src/app.css` | Shared colors, fonts, focus behavior, and page-wide styling. |

## Current user flow

```text
Choose a corpus example
        |
        v
Source textarea receives Cebuano text
        |
        v
Select model and press "Translate to Tagalog"
        |
        v
Local demo lookup returns the matching Tagalog text
        |
        +--> No match: show an honest demo limitation message
```

The Translate button remains unavailable until a model has loaded and the user
has entered text. Result changes are announced to assistive technology through
an ARIA live region.

## Important limitation

The browser interface currently does **not** call `main.py`, load NLLB, or use
the models saved in `models/`. The Python CLI and the Svelte frontend are two
separate experiences right now.

That means this is accurate:

- The Python CLI can perform model-based translation after the required model is
  available.
- The frontend can demonstrate only the examples in `frontend/src/lib/api.js`.

That distinction matters when presenting the project: do not describe the web
demo as live NLLB translation until it is connected to a backend.

## Next step: connect real translation

To turn the demo into a real web translator, add an HTTP API around the Python
translation pipeline, then replace the local functions in `frontend/src/lib/api.js`.

The browser-side contract can stay small:

```text
GET  /api/models
POST /api/translate
     { "model_name": "...", "source_text": "..." }
     -> { "translated_text": "..." }
```

Before implementing this, agree on where the model will run. NLLB is large, so
the backend should own model loading and inference; the browser should never
download model weights. Keep the frontend's loading, error, and empty-result
states when making that change.

## Working together

- Make frontend changes inside `frontend/`.
- Run `npm run build` before handing off frontend work.
- Make Python/model changes in the root project and run `python -m pytest -q`.
- Update this guide when the frontend stops being a local demo or when the API
  contract changes.

