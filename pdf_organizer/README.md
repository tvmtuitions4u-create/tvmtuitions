# PDF Organizer — Flask Project Proposal & Implementation

A lightweight, self-hosted **document repository** for managing PDFs and other files (notes, slides, assignments, etc.) with rich optional metadata, powerful search/filter, full CRUD, and the ability to generate a **static HTML catalog** for public or offline sharing.

## Problem It Solves

Teachers, tutors, coaching centers, and students need a simple way to:
- Store class materials organized by **subject**, **batch**, **daily class**, and **students**
- Quickly find a specific lecture PDF later
- Keep optional details (tags, notes, class date, audience)
- Share a searchable catalog without giving database access
- Support both PDFs and other file types

## Core Features

### 1. Upload with Flexible Metadata
- File upload (PDF, DOC/DOCX, PPT, TXT, images, ZIP — max 50 MB)
- Required: Title + File
- Optional fields:
  - Subject
  - Batch / Group
  - Class / Lecture name (daily class)
  - Class date
  - Students / Audience
  - Description
  - Tags (comma-separated)
  - Category (PDF, Notes, Slides, Assignment, Other)
  - Additional notes

### 2. Full CRUD
- Create (upload)
- Read (library list + detail view)
- Update (edit any metadata)
- Delete (removes file + record)

### 3. Search & Filter
- Full-text search across title, description, tags, subject, class name, notes, filename
- Filters: Subject, Batch, Category, Class date range
- Autocomplete suggestions from existing values

### 4. Static Site Generation
- Live “Static Catalog” page with client-side instant search
- One-click **Export Static** generates a completely self-contained `static/pdf_catalog.html`
  - Embeds all metadata as JSON
  - Works offline
  - Instant search/filter in the browser
  - No server required after export

### 5. Extra
- Download original files
- Clean Bootstrap 5 UI
- SQLite database (zero config)
- REST-style JSON API endpoint (`/api/documents`)

## Tech Stack

- **Backend**: Flask 3 + SQLAlchemy
- **Database**: SQLite (easy to migrate to Postgres later)
- **Frontend**: Bootstrap 5 + vanilla JS
- **Deployment**: Single folder, run with `python app.py`

## Project Structure

```
pdf_organizer/
├── app.py                  # Main Flask application
├── models.py               # Document model
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html          # Library + search
│   ├── upload.html
│   ├── detail.html
│   ├── edit.html
│   ├── static_catalog.html
│   └── static_catalog_export.html
├── static/
│   └── pdf_catalog.html    # Generated static site
├── uploads/                # Stored files
└── README.md
```

## Quick Start

```bash
cd pdf_organizer
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Future Optional Enhancements

- User authentication & roles (admin / teacher / student)
- Folder / hierarchical organization
- Bulk upload
- Full-text search inside PDF content (using PyPDF2 / pdfminer)
- Thumbnail generation
- Versioning of documents
- Email / share links
- Dark mode
- Docker support
- Export to CSV / JSON

## Why This Design

- **Optional-heavy metadata**: Most fields are optional so daily use stays fast, while power users can add rich details.
- **Static export**: Perfect for sharing a searchable library with students without exposing the admin interface or database.
- **Simple stack**: Easy to understand, extend, and deploy on any cheap VPS or even a Raspberry Pi.
- **CRUD + Search first**: The most requested operations for a personal/class document repository.

---

**This is a ready-to-run prototype** of the proposed system. You can start uploading materials immediately and refine the optional fields or UI as needed.
