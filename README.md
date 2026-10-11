# CyberAcademy Course Studio

Python/Flask course management with SQLite persistence and CyberAcademy Course XML 1.0 interchange. Built from the supplied format documentation; no original Python importer or formal XSD was supplied.

## Run

```sh
cd /workspace/cyber-courses-codex
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Open the application on port 5000 and create the first administrator (12-character minimum password). First-time setup should be completed in a trusted environment before exposing the server publicly. Data and a private session key live in ignored `instance/`; back up that directory. `PORT` can change the listening port. The bundled Flask server is for development; production requires a WSGI server, HTTPS, secure cookie configuration, login rate limiting, and deployment-specific access controls.

## Use

- Create a course, edit metadata, and toggle publication, free access, featured status, or certification.
- Add/edit/delete lessons with content, video, images, lab instructions, quiz questions and correct answers, and link or uploaded resources. Save lessons into the editor, then **Save course** to persist the complete course.
- Export by row or exact full course name. Import one XML file, optionally pruning absent lessons. A summary reports created/updated lessons, restored files, and removals.
- Search the catalog and filter by publication status. Delete prompts for confirmation.

XML exports use the supplied namespace and version, preserve text including CDATA content (serialized as equivalent escaped XML), and embed uploaded files in base64. Imports match course slug then case-insensitive title, preserve existing course slugs, conservatively merge course metadata, replace matching lessons, and prune only when at least one valid lesson is supplied. Counts and duration are recomputed. Instructor references resolve to an existing administrator profile by email; imports never create accounts. Categories are preserved as embedded name/slug metadata rather than a separate catalog.

DTDs and entities are rejected. XML depth is capped at 256; total request size at 256 MB; embedded files at or above 32 MB are skipped on import. Invalid XML/base64 fails before persistence. Writes use SQLite transactions. Downloaded resources are served as attachments. UI text is escaped and remote images accept only HTTP(S). No HTML lesson rendering or automatic execution of labs occurs.

## API

Session authentication and an `X-CSRF-Token` header protect writes. Obtain a CSRF token from `GET /api/session`, then use `POST /api/auth/setup` or `/api/auth/login` with email/password JSON. This standalone application uses session cookies rather than the original project's JWTs.

- `GET/POST /api/courses`: list/create `{course, lessons}` packages.
- `PUT/DELETE /api/courses/<id>`: update/delete.
- `GET /api/admin/course-packages/export?courseId=...` or `?name=...`.
- `POST /api/admin/course-packages/import`: multipart `file` and `replace=true|false`.
- `GET /api/courses/<id>/lessons/<id>/resources/<index>`: embedded resource download.

## Validate

```sh
.venv/bin/python -m unittest discover -s tests -v
node --check static/app.js
```

Tests cover CRUD, auth/CSRF, all XML model fields, embedded file downloads, round trips, merge/pruning safeguards, invalid input rollback, and malicious XML rejection.

## Seeded ISO/IEC 27001 introduction

The database includes **Introduction to ISO 27001 ISM**: 10 lessons, 10 practical labs, 30 quiz questions, 10 embedded original worksheets, and 49 resource entries. Total estimated learning time: 12.75 hours, including activities. The published course uses ISO/IEC 27001:2022 with Amendment 1:2024 and explains the 31 October 2025 certification-transition milestone. It also identifies NIST SP 800-61 Rev. 3 (2025) as supplementary incident-response guidance. No ISO/IEC 27001:2025 edition is claimed.

Official ISO/IAF/NIST links and user-supplied https://www.iso27001security.com/ are included as reading resources. Live retrieval of these sites was blocked by the environment proxy at authoring time, so the original summaries and questions must not be described as quotations or freshly verified web research. Verify links and exact requirements when network access is available; normative ISO text requires licensed access. Community guidance is supplementary.

Portable course: `seeds/iso27001-introduction.course.xml`. Editable source data: `seeds/iso27001-introduction.json`. Generate artifacts with `.venv/bin/python scripts/build_iso_course.py`. Seed an initialized local application database with `.venv/bin/python scripts/seed_iso_course.py`. The seed makes a SQLite backup and inserts only if neither slug nor title exists. Re-running preserves user edits and does not create duplicates. It does not create an administrator account. The XML can also be imported through the normal administrator UI.

## Temporary online demonstration

`render.yaml` describes a Render Python web service requesting the free plan (subject to Render availability and account eligibility). Deploy a Blueprint from this repository through your Render account. The generated `PREVIEW_PASSWORD` is visible in the service's environment settings; the access username is `preview`. After passing this HTTP Basic password gate, create the application's administrator account. This gate protects all routes, including first-time setup and course downloads. HTTPS is supplied by the hosting service. No hosting credentials are stored in this repository.

The start command initializes the database and seeds the ISO course before starting Gunicorn. Render free service filesystems are ephemeral: edits and administrator accounts may be lost on a redeploy/restart, and the service may sleep. Export modified courses before stopping it. This configuration is for a temporary demo, not durable hosting. The deployed database is newly initialized; local private database backups and credentials are not uploaded.

A local protected instance can run with `.venv/bin/gunicorn --bind 127.0.0.1:5001 --workers 1 --threads 4 scripts.temporary_server:require_access` after setting `PREVIEW_PASSWORD` securely or initializing ignored `instance/temporary-access.json`. Use a strong unique password. Cloudflare Quick Tunnel was attempted during setup but failed: direct connectivity was refused and the API returned HTTP 403 through the environment proxy. No public tunnel URL was issued.
