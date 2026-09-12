# SalinWika Web

This is the frontend-only interface for the Cebuano-to-Tagalog translator.
It runs as a standalone Svelte app and does not require the FastAPI backend
service to be running.

## Current setup

The web interface is now designed as a local demo interface:

- no backend is required to open the app
- sample Cebuano phrases load directly in the browser
- the model picker and translation output are populated from local demo data
- the UI is ready for a future real model integration

## Project structure

```text
salinwika/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── backend/
│   └── ...
├── README.md
├── README copy.md
├── config.yaml
└── main.py
```

## Run locally

From the frontend folder:

```bash
cd frontend
npm install
npm run dev 
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:5173
```

## Notes

This is intentionally a presentation/demo interface. The backend code remains
in the repository for future restoration, but the current UI is self-contained
and can be used without the service layer.

## Planned next step

If a real model backend is added later, the frontend can be wired to a real
translation endpoint without changing the current layout or UI design.
