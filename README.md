# resy-book-bot
Customizable booking bot for Resy based on submitted time intervals.

A bot designed to create reservations based on given time intervals on [Resy](https://resy.com/) using the
[ResyAPI](http://subzerocbd.info/). Given a selected restaurant and time, when reservations become available
the bot will search and attempt to book.

## Flask entry point
The backend lives under `backend/app`. The module exposes `create_app()` in `app/__init__.py` which configures
Firebase, Firestore and Cloud Tasks clients and registers all Flask blueprints. `wsgi.py` simply imports and
runs this factory:

```python
from app import create_app
app = create_app()

if __name__ == "__main__":
    app.run()
```

## Major routes
### `/resy`
- `POST /resy/search` – search for venues. Requires `uid` query param or `RESY-AUTH-TOKEN` header.
  Form fields: `lat`, `lon`, `day` (`YYYY-MM-DD`), `party_size`.
- `GET /resy/venue-details` – get details for a venue using `venue_id` query param and `RESY-AUTH-TOKEN` header.
- `POST /resy/create` – schedule a reservation. Form fields:
  `uid`, `resLiveDate` (`YYYY-MM-DD HH:MM:SS`), `resDay` (`YYYY-MM-DD`), `partySize`, `venue_id` and one or
  more `resTimes` entries (`HH:MM`).

### `/resy-bot`
Called internally by Cloud Tasks.
- `POST /resy-bot/execute` – attempts to book a reservation. Payload fields include `uid`, `res_day`,
  `venue_id`, `party_size`, `res_times`, and a Resy auth `token`.
- `POST /resy-bot/check-auth` – verifies a stored Resy token. Payload fields: `uid` and `task_type`=`auth_check`.

### `/user`
- `POST /user/register` – registers a new user with `email`, `password`, `first_name` and `phone_number`.
- `POST /user/authorize-resy` – saves a Resy auth token for the supplied `email`.
- `POST /user/delete-resy-token` – removes a saved token for `email`.
- `GET /user/user-profile` – returns active tasks and token information for `userId`.
- `GET /user/check-token` – validates the stored token for `userId`.

### `/meta-api`
- `POST /meta-api/create-issue` – creates a GitHub issue. Form fields: `title`, `body`, `level`.

## Google Cloud Tasks & Firebase
`TaskHandler` uses Google Cloud Tasks to schedule background requests to the `/resy-bot` endpoints. When a
reservation watch is created, a Cloud Task is scheduled to hit `/resy-bot/execute` at the moment reservations
go live. Another task may be scheduled to run `/resy-bot/check-auth` before that time to validate the user's
Resy token.

`AccountHandler` integrates with Firebase Authentication and Firestore. New users are stored using Firebase
Auth, and their Resy tokens and pending reservation tasks are kept in Firestore collections. Firestore is also
used to queue notification emails.

