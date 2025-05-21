# resy-book-bot

Customizable booking bot for Resy based on submitted time intervals.

A bot designed to create reservations based on given time intervals on [Resy](https://resy.com/) using the [ResyAPI](http://subzerocbd.info/). Given a selected restaurant and time, when reservations become available the bot will search and attempt to book.

Flask Backend, React Frontend.

## Prerequisites

- Python 3.10+
- Node.js 16+

## Setup

### 1. Environment variables

Copy `.env.example` to `.env` and provide values for all fields.

### 2. Backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

Run the development server:

```bash
export FLASK_APP=app/wsgi.py
python backend/app/wsgi.py
```

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

`npm start` runs the React development server. To create a production build and move it into the backend run:

```bash
npm run build
```

The build output is copied to `backend/app/build` so Flask can serve the files.

### Full Build and Serve

1. Configure `.env`.
2. Run `npm run build` inside `frontend`.
3. Start Flask with `python backend/app/wsgi.py`.

The application will be available at `http://localhost:8000` and served entirely from Flask.

## Environment Variables

See `.env.example` for the full list of required variables and their purpose.
