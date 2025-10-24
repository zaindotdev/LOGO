# ecom — Django e-commerce example

This repository contains a small Django e-commerce application used for learning and development. The project includes simple apps for accounts, products, cart, orders and pages (static pages).

## Table of Contents
- About
- Installed apps
- Requirements
- Quick start (Windows PowerShell)
- Environment & configuration
- Database
- Running
- Tests
- Static files & media
- Project structure
- Contributing
- License
- Contact

## About
This is an e-commerce example project (project package: `ecom`). It uses Django's standard patterns and a small set of apps to demonstrate product pages, a shopping cart, checkout and user accounts.

## Installed apps (in this repo)
- `accounts` — user registration & auth views/templates
- `products` — product models and product detail pages
- `cart` — shopping cart and cart views
- `orders` — checkout and order models/views
- `pages` — site pages (home, about, contact)
- `ecom` — project package (settings, urls, wsgi/asgi)

These apps live at the top level of the repository (see "Project structure").

## Requirements
- Python 3.8+
- pip
- virtualenv (recommended)

If you need a specific Django version, check `pyproject.toml` / `requirements.txt` or run `pip show Django` in your environment. If none is present, Django 4.2+ is a safe, supported choice for new projects.

## Quick start — Windows PowerShell
Open PowerShell in the repository root (`d:\Projects\DJANGO_ASSIGNMENT`) and run the following commands.

```powershell
# create virtual environment and activate
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# install requirements (create requirements.txt if missing)
pip install -r requirements.txt

# copy example env and edit if needed
copy .env.example .env

# apply migrations and create a superuser
python manage.py migrate
python manage.py createsuperuser

# run the development server
python manage.py runserver
```

If you prefer cmd.exe instead of PowerShell, activate the venv with ` .\.venv\Scripts\activate`.

## Environment & configuration
This project supports configuring sensitive values via environment variables or a `.env` file. Create `.env` from `.env.example` and set values for production.

Common variables
- SECRET_KEY — Django secret key
- DEBUG — True or False
- ALLOWED_HOSTS — comma-separated hosts
- DATABASE_URL — optional (defaults to SQLite)
- EMAIL settings — if your app sends emails

Example `.env` lines:

```
SECRET_KEY=replace-me-with-a-secure-value
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Database
- Development: SQLite file at project root (`db.sqlite3`).
- Production: use PostgreSQL or another production-ready DB (set `DATABASE_URL`).

Apply migrations:

```powershell
python manage.py migrate
```

## Running

Start the development server (automatically serves static files when DEBUG=True):

```powershell
python manage.py runserver
```

For production, run behind a WSGI server (Gunicorn/uvicorn) and reverse proxy (nginx). Example:

```bash
gunicorn ecom.wsgi:application
```

## Tests

Run the test suite:

```powershell
python manage.py test
```

If you add CI, configure the runner to run the above command on push/PR.

## Static files & Media
- Static files for each app live under each app's `static/` folder (for example `products/static/`, `pages/static/`). A global `static/` directory is present as well.
- Media (uploaded files) are stored in `media/`. Example product images live under `media/products/2025/10/...` in this workspace.

Collect static for production:

```powershell
python manage.py collectstatic --noinput
```

## Project structure (relevant files/folders)

- `manage.py` — Django CLI
- `db.sqlite3` — development database (SQLite)
- `ecom/` — project package (settings, urls, wsgi, asgi)
- `accounts/`, `products/`, `cart/`, `orders/`, `pages/` — app packages
- `media/` — uploaded media files
- `static/` — global static assets
- `templates/` — base templates (layout, etc.)

Refer to each app's folder for templates and static subfolders (e.g., `cart/templates/cart.html`, `products/templates/product.html`).

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository
2. Create a feature branch
3. Add tests for new behavior
4. Open a pull request

Keep changes small and focused. Update the README if you add new developer-facing features.

## License

Add a `LICENSE` file to the project root and reference it here (e.g., MIT, Apache 2.0).

## Contact

Open issues in the repository for bugs or features. Include reproduction steps and any relevant logs.

---

If you'd like, I can also:
- create a `.env.example` file with the variables above
- add a minimal `requirements.txt` (I can infer a Django version or you can tell me which to use)
- create a simple `Dockerfile` and `docker-compose.yml` for local development

Tell me which of those you'd like me to add next.