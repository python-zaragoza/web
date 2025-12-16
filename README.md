# Python Zaragoza — Community website

Official website of the **Python Zaragoza** community built with
[Reflex](https://reflex.dev/) and managed with
[uv](https://docs.astral.sh/uv/).

![PyZgz Logo](assets/logo.png)

## 🚀 What is Python Zaragoza?

Python Zaragoza is a local community of people interested in **Python** in Zaragoza. We organize:

- 📅 **Meetups**: talks and networking.
- 🛠️ **Workshops**: hands-on sessions for all levels.
- 🤝 **Projects**: open and collaborative initiatives.

Our goal is to promote the use and learning of Python in an open and friendly environment.

------------------------------------------------------------------------

## 📂 Project structure

    .
      ├── assets/          # Static assets (logo, favicon, generated data)
      ├── pyzgz/           # Reflex application code
      │   ├── main.py      # App entry point (App & routes)
      │   ├── layout.py    # Shared layout (nav, footer, page_wrapper, styles)
      │   ├── index_page.py
      │   ├── events_page.py
      │   ├── blog_page.py
      │   ├── comunity_page.py
      │   ├── talks_page.py
      │   ├── about_page.py
      │   └── contact_page.py
      ├── rxconfig.py      # Reflex configuration
      ├── pyproject.toml   # Dependencies and metadata (Python >=3.11)
      ├── uv.lock          # Locked dependencies (uv)
      └── README.md

Note: the site is prepared for static deployment on GitHub Pages.

------------------------------------------------------------------------

## 🛠️ Local development

0. **Prerequisites:**

    - Python 3.11 or newer.
    - uv installed. See <https://docs.astral.sh/uv/getting-started/installation/> (e.g., `pipx install uv`).

1. **Clone the repository and go to `web/`:**

    ``` bash
    git clone <url_del_repo>
    cd <repo>
    cd web
    ```

2. **Install dependencies with uv:**

    ``` bash
    uv sync
    ```

3. **Start the dev server:**

    ``` bash
    uvx reflex run
    ```

    Then open <http://localhost:3000>.

4. **Cache cleanup (if HMR behaves oddly):**

    ``` bash
    rm -rf .web
    ```

------------------------------------------------------------------------

## 🌐 Deployment

### GitHub Pages (static)

1. Build the site:

    ``` bash
    uvx reflex export --frontend-only
    ```

    This creates a `./.web/_static` directory with files ready to publish.

2. Configure a GitHub Actions workflow to:

    - Run `uvx reflex export --frontend-only`.
    - Publish `./.web/_static` to GitHub Pages.

Tip: create a workflow that builds on every push to `main` and uploads `./.web/_static` as a Pages artifact.

------------------------------------------------------------------------

## 📬 Contact and Talks

- **Propose a talk (CFP):** send your proposal to `zaragoza@es.python.org`.
  Include title, abstract, approximate duration and level.
- **General contact:** `zaragoza@es.python.org`.

### Talks form (Google Forms)

The `Charlas` page links to a **Google Form**:

- Current link: `https://forms.gle/qvMCiq8GkyCty79N8` (configurable in `pyzgz/talks_page.py`, constant `GOOGLE_FORM_URL`).
- Alternatively, email us at `zaragoza@es.python.org`.

------------------------------------------------------------------------

## ⚙️ Configuration

For static deployment on GitHub Pages **no environment variables are required**.
If backend/APIs get integrated in the future, they will be documented here.

### Meetup events

- **Group**: `python_zgz`.
- **Without token**: the build uses the public iCal feed and generates `assets/events.json` with upcoming events only.
- **With token (optional)**: add a `MEETUP_TOKEN` secret in the repo so the workflow also fetches past events via the API.
- **Workflow**: `.github/workflows/pages.yml` runs `scripts/fetch_meetup.py` before `reflex export`.
- **Local test**:
  ```bash
  # Generate events.json (without token uses iCal)
  uv run python scripts/fetch_meetup.py
  # Run the site
  uvx reflex run
  ```

------------------------------------------------------------------------

## 📜 License

[MIT](LICENSE)

------------------------------------------------------------------------

## 🗺️ Roadmap

- [x] **Initial pages structure**: home, community, about, contact, blog, events, talks (CFP).
- [ ] **Persistent status messages**: better UX when navigating between pages.
- [ ] **Fetch Meetups**:
  - Server: consume API with `MEETUP_TOKEN`.
  - Static: prebuild `assets/events.json` in GitHub Actions.
- [ ] **SEO & accessibility**: meta tags, OpenGraph, manifest, favicon.
- [ ] **Visual design improvements**: light/dark theme, custom styles.
- [ ] **Automated deployment** on GitHub Pages with a stable workflow.
- [ ] **Optional** English/Spanish i18n.

------------------------------------------------------------------------

**Made with ❤️ in Zaragoza.**

------------------------------------------------------------------------

## 🤝 Contributing

- **Dev dependencies** are declared under the `dev` group in `pyproject.toml` (ruff, black, pre-commit, pytest).
- **Setup**:
  ```bash
  uv sync --group dev
  uv run pre-commit install
  ```
- **Run linters/formatters manually**:
  ```bash
  uv run ruff check --fix .
  uv run ruff format .
  uv run black .
  ```
- **Run hooks on all files**:
  ```bash
  uv run pre-commit run --all-files
  ```
- **Tests** (placeholder):
  ```bash
  uv run pytest -q
  ```
