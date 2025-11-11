import reflex as rx
import os
import json
import re
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Tuple

# ---------- Base styles ----------
BASE_FONT = "system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif"
styles = {
    "global": {"font_family": BASE_FONT, "line_height": "1.5", "color": "black"},
    "container": {"max_width": "1100px", "margin_x": "auto", "padding_x": ["1rem", "1.5rem", "2rem"]},
    "section": {"padding_y": ["2rem", "3rem"]},
}

# ---------- Persistence (CFP) ----------
DATA_DIR = "data"
CFP_FILE = os.path.join(DATA_DIR, "cfp.json")
MAX_CFP_FILE_BYTES = 2_000_000  # ~2 MB safety limit
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Ensure data directory exists.
os.makedirs(DATA_DIR, exist_ok=True)


def _safe_read_json_list(path: str) -> List[Dict[str, Any]]:
    """Read a JSON file that should contain a list; return [] on any problem.

    This avoids throwing on common issues (missing file, invalid JSON, wrong root type).
    """
    if not os.path.exists(path):
        return []
    try:
        if os.path.getsize(path) > MAX_CFP_FILE_BYTES:
            # Do not try to read extremely large files to prevent memory issues.
            return []
    except OSError:
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _safe_write_json_atomic(path: str, payload: Any) -> None:
    """Write JSON atomically to avoid partial writes.

    Writes to a temporary file first, then atomically replaces the target.
    """
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(payload, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    finally:
        # If something went wrong before os.replace, ensure the tmp file is removed.
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception:
            pass


def _validate_cfp(form: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Validate CFP form fields. Returns (is_valid, errors)."""
    title = (form.get("title") or "").strip()
    speaker = (form.get("speaker") or "").strip()
    email = (form.get("email") or "").strip()
    level = (form.get("level") or "").strip()
    duration_raw = (form.get("duration") or "").strip()
    abstract = (form.get("summary") or "").strip()

    errors: List[str] = []

    if not title:
        errors.append("El título es obligatorio.")
    if not speaker:
        errors.append("El nombre del ponente es obligatorio.")
    if not email:
        errors.append("El email es obligatorio.")
    if not level:
        errors.append("El nivel es obligatorio.")
    elif not EMAIL_RE.match(email):
        errors.append("El email no tiene un formato válido.")
    if not abstract:
        errors.append("El resumen es obligatorio.")

    if duration_raw:
        # Allow only positive integers for duration (in minutes).
        if not duration_raw.isdigit() or int(duration_raw) <= 0:
            errors.append("La duración debe ser un número entero positivo (minutos).")
    return (len(errors) == 0, errors)


# ---------- State ----------
class CFPState(rx.State):
    """Server-side state for handling CFP submissions."""
    notice: str = ""
    error: str = ""

    def clear(self):
        """Clear transient status messages."""
        self.notice = ""
        self.error = ""

    def submit(self, form_data: Dict[str, Any]):
        """Handle CFP form submission and persist into data/cfp.json (append).

        Steps:
          1) Validate required fields (title, speaker, email, abstract).
          2) Optional fields (level, duration) are normalized.
          3) Append to an in-memory list and write atomically to JSON.
        """
        # Clear previous messages.
        self.notice = ""
        self.error = ""

        try:
            is_valid, errors = _validate_cfp({k: str(v) for k, v in form_data.items()})
            if not is_valid:
                # Join multiple validation errors into a single message.
                self.error = " ".join(errors)
                return

            # Build normalized payload.
            title = (form_data.get("title") or "").strip()
            speaker = (form_data.get("speaker") or "").strip()
            email = (form_data.get("email") or "").strip()
            level = (form_data.get("level") or "").strip()
            duration_raw = (form_data.get("duration") or "").strip()
            duration = int(duration_raw) if duration_raw.isdigit() else None
            summary = (form_data.get("summary") or "").strip()

            payload = {
                "title": title,
                "speaker": speaker,
                "email": email,
                "level": level or None,
                "duration": duration,
                "summary": summary,
                "created_at": datetime.utcnow().isoformat() + "Z",
            }

            # Load, append, write atomically.
            existing = _safe_read_json_list(CFP_FILE)
            existing.append(payload)
            _safe_write_json_atomic(CFP_FILE, existing)

            self.notice = "¡Gracias! Hemos recibido tu propuesta."
            self.error = ""
        except Exception as e:
            # Show a concise message to the user; keep details on server logs if needed.
            self.error = "Error al guardar la propuesta. Inténtalo de nuevo más tarde."
            # Optional: print server-side details for debugging
            print(f"[CFPState.submit] Unexpected error: {e!r}")


class ContactState(rx.State):
    notice: str = ""
    error: str = ""

    def clear(self):
        """Clear transient status messages."""
        self.notice = ""
        self.error = ""

    def submit(self, form_data: dict):
        """Handle contact form submission (validate + (optionally) email/save)."""
        self.notice = ""
        self.error = ""

        name = (form_data.get("nombre") or "").strip()
        email = (form_data.get("email") or "").strip()
        message = (form_data.get("mensaje") or "").strip()

        # minimal validation
        if not name or not email or not message:
            self.error = "Nombre, email y mensaje son obligatorios."
            return
        if not EMAIL_RE.match(email):
            self.error = "El email no tiene un formato válido."
            return

        # TODO: here you can save to a file/DB or send an email.
        # For now, just ack:
        self.notice = "¡Gracias! Hemos recibido tu mensaje."

# ---------- Layout ----------
def nav():
    return rx.box(
        rx.hstack(
            rx.link(
                "Python Zaragoza",
                href="/",
                font_weight="bold",
                font_size="1.25rem",
                on_click=[CFPState.clear, getattr(rx, "noop", lambda: None)]
            ),
            rx.spacer(),
            rx.hstack(
                rx.link("Eventos", href="/events", on_click=[CFPState.clear, ContactState.clear]),
                rx.link("Blog", href="/blog", on_click=[CFPState.clear, ContactState.clear]),
                rx.link("Comunidad", href="/comunity", on_click=[CFPState.clear, ContactState.clear]),
                rx.link("Charlas", href="/talks", on_click=[CFPState.clear, ContactState.clear]),
                rx.link("Sobre", href="/about", on_click=[CFPState.clear, ContactState.clear]),
                rx.link("Contacto", href="/contact", on_click=[CFPState.clear, ContactState.clear]),
                spacing="4",
                display=["none", "flex"],
            ),
            # Mobile menu
            rx.box(
                rx.menu.root(
                    rx.menu.trigger(rx.button("Menú")),
                    rx.menu.content(
                        rx.menu.item(
                            "Eventos",
                            on_click=[CFPState.clear, ContactState.clear, rx.redirect("/events")],
                        ),
                        rx.menu.item(
                            "Blog",
                            on_click=[CFPState.clear, ContactState.clear, rx.redirect("/blog")],
                        ),
                        rx.menu.item(
                            "Comunidad",
                            on_click=[CFPState.clear, ContactState.clear, rx.redirect("/comunity")],
                        ),
                        rx.menu.item(
                            "Charlas",
                            on_click=[CFPState.clear, ContactState.clear, rx.redirect("/talks")],
                        ),
                        rx.menu.item(
                            "Sobre",
                            on_click=[CFPState.clear, ContactState.clear, rx.redirect("/about")],
                        ),
                        rx.menu.item(
                            "Contacto",
                            on_click=[CFPState.clear, ContactState.clear, rx.redirect("/contact")],
                        ),
                    ),
                ),
                display=["inline-flex", "none"],
            ),
            width="100%",
            align="center",
        ),
        style={"border_bottom": "1px solid #eee", "padding": "0.75rem 0"},
    )



def footer():
    """Footer with social links."""
    return rx.box(
        rx.vstack(
            rx.text("© 2025 PythonZgz · Comunidad Python en Zaragoza"),
            rx.hstack(
                rx.link("Telegram", href="https://t.me/python_zgz", is_external=True),
                rx.text("·"),
                rx.link("Meetup", href="https://www.meetup.com/es-ES/python_zgz/", is_external=True),
                spacing="2",
                wrap="wrap",
                justify="center",
            ),
            spacing="2",
            align="center",
        ),
        style={"border_top": "1px solid #eee", "padding": "1.25rem 0", "margin_top": "2rem"},
    )


def page_wrapper(*children):
    """Shared page wrapper that applies global container, nav, and footer."""
    return rx.box(nav(), rx.box(*children, style=styles["container"]), footer())


# ---------- Pages ----------
def index():
    """Home page."""
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.image(src="/logo.png", alt="Logo PythonZgz", width="200px", height="auto"),
                rx.heading("Comunidad Python Zaragoza", size="8"),
                rx.text(
                    "Charlas, talleres y quedadas para aprender y compartir Python en Zaragoza.",
                    text_align="center",
                    max_width="40rem",
                ),
                rx.hstack(
                    rx.link(rx.button("Próximos eventos"), href="/events"),
                    rx.link(rx.button("Propón una charla", variant="outline"), href="/talks"),
                    spacing="3",
                    wrap="wrap",
                    justify="center",
                ),
                spacing="4",
                align="center",
            ),
            style=styles["section"],
        ),
        rx.section(
            rx.vstack(
                rx.heading("¿Qué hacemos?"),
                rx.grid(
                    rx.card(
                        rx.vstack(
                            rx.heading("Meetups", size="4"),
                            rx.text("Charlas, demos y networking."),
                            spacing="2",
                        )
                    ),
                    rx.card(
                        rx.vstack(
                            rx.heading("Talleres", size="4"),
                            rx.text("Sesiones prácticas."),
                            spacing="2",
                        )
                    ),
                    rx.card(
                        rx.vstack(
                            rx.heading("Proyectos", size="4"),
                            rx.text("Iniciativas abiertas."),
                            spacing="2",
                        )
                    ),
                    columns={"base": "1", "md": "3"},
                    gap="4",
                ),
                spacing="4",
                align="center",
            ),
            style=styles["section"],
        ),
    )


def events():
    """Events page (static placeholder; will integrate Meetup later)."""
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Eventos"),
                rx.text("Listaremos próximos eventos y el histórico. Integraremos Meetup más adelante."),
                rx.link("Ir a nuestro Meetup →", href="meetup.com/es-ES/python_zgz/", is_external=True),
                spacing="3",
            ),
            style=styles["section"],
        )
    )


def blog():
    """Blog page placeholder."""
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Blog"),
                rx.text("Notas de charlas, tutoriales y crónicas."),
                spacing="3",
            ),
            style=styles["section"],
        )
    )


def comunity():
    """Community page with social links."""
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Comunidad"),
                rx.text("Únete a nuestros canales:"),
                rx.list(
                    rx.list_item(rx.link("Telegram", href="https://t.me/python_zgz", is_external=True)),
                    rx.list_item(rx.link("Meetup", href="meetup.com/es-ES/python_zgz/", is_external=True)),
                ),
                spacing="3",
            ),
            style=styles["section"],
        )
    )


def talks():
    """CFP page. Stores talk proposals into data/cfp.json."""
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Propón una charla"),
                rx.text("Rellena el formulario y nos pondremos en contacto contigo."),
                rx.text("Todos los campos son obligatorios"),
                rx.cond(CFPState.error != "", rx.callout(text=CFPState.error, color_scheme="red", variant="soft")),
                rx.cond(CFPState.notice != "", rx.callout(text=CFPState.notice, color_scheme="green", variant="soft")),
                rx.form(
                    rx.vstack(
                        rx.input(placeholder="Título de la charla", name="title", required=True, width="100%"),
                        rx.input(placeholder="Ponente (tu nombre)", name="speaker", required=True, width="100%"),
                        rx.input(placeholder="Email de contacto", type="email", name="email", required=True, width="100%"),
                        rx.input(placeholder="Nivel (intro, intermedio, avanzado)", name="level", required=True, width="100%"),
                        rx.input(placeholder="Duración (minutos)", type="number", required=True, width="100%"),
                        rx.input(placeholder="Resumen", name="summary", required=True, width="100%"),
                        rx.text_area(placeholder="Mensaje", name="mensaje", required=True, rows="6", width="100%"),
                        rx.button("Enviar", width="100%"),
                        spacing="3",
                        width="100%",
                        max_width="42rem",
                    ),
                    on_submit=CFPState.submit,
                    reset_on_submit=True,
                    width="100%",
                ),
                spacing="4",
                align="center",
            ),
            style=styles["section"],
        )
    )



def about():
    """About page."""
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Sobre Python Zaragozaz"),
                rx.text(
                    "Comunidad abierta y sin ánimo de lucro. Promovemos Python en Zaragoza mediante eventos y recursos.",
                    max_width="48rem",
                ),
                spacing="3",
            ),
            style=styles["section"],

        )
    )


def contact():
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Contacto"),
                rx.text("Propón charlas, locales o colaboración."),
                # status messages
                rx.cond(ContactState.error != "", rx.callout(text=ContactState.error, color_scheme="red", variant="soft")),
                rx.cond(ContactState.notice != "", rx.callout(text=ContactState.notice, color_scheme="green", variant="soft")),
                rx.form(
                    rx.vstack(
                        rx.input(placeholder="Tu nombre", name="nombre", required=True, width="100%"),
                        rx.input(placeholder="Tu email", type="email", name="email", required=True, width="100%"),
                        rx.text_area(placeholder="Mensaje", name="mensaje", required=True, rows="6", width="100%"),
                        rx.button("Enviar", width="100%"),
                        spacing="3",
                        width="100%",
                        max_width="42rem",
                    ),
                    on_submit=ContactState.submit,
                    reset_on_submit=True,
                    width="100%",
                ),
                spacing="4",
                align="center",
            ),
            style=styles["section"],
        )
    )


# ---------- App & routes ----------
app = rx.App(theme=rx.theme(appearance="dark"))
app.add_page(index, route="/", title="PythonZgz — Comunidad Python Zaragoza")
app.add_page(events, route="/events", title="Eventos · PythonZgz")
app.add_page(blog, route="/blog", title="Blog · PythonZgz")
app.add_page(comunity, route="/comunity", title="Comunidad · PythonZgz")
app.add_page(talks, route="/talks", title="Proponer charla · PythonZgz")
app.add_page(about, route="/about", title="Sobre · PythonZgz")
app.add_page(contact, route="/contact", title="Contacto · PythonZgz")
