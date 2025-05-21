# Development Guide

## Prerequisites
- Python 3.11
- Node.js (v16+)

## Setup
Install Python dependencies:
```bash
pip install -r backend/requirements.txt
pip install -r requirements-dev.txt
```

Install frontend dependencies:
```bash
cd frontend
npm install
```

## Code Quality
Run formatters and linters before committing:
```bash
black backend/app
ruff check backend/app
npm run lint
```

`black` formats Python code and `ruff` lints it. `npm run lint` runs ESLint on the React source.
