import reflex as rx
from reflex.style import set_color_mode, color_mode

BASE_FONT = "system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif"
styles = {
    # No fijamos color global; dejamos que el tema controle el color según el modo
    "global": {"font_family": BASE_FONT, "line_height": "1.6"},
    "container": {
        "max_width": "1100px",
        "margin_x": "auto",
        "padding_x": ["1rem", "1.5rem", "2rem"],
    },
    "section": {"padding_y": ["2rem", "3rem"]},
}

EMAIL = "zaragoza@es.python.org"


def dark_mode_toggle() -> rx.Component:
    return rx.segmented_control.root(
        # rx.segmented_control.item(
        #     rx.icon(tag="monitor", size=20),
        #     value="system",
        # ),
        rx.segmented_control.item(
            rx.icon(tag="sun", size=20),
            value="light",
        ),
        rx.segmented_control.item(
            rx.icon(tag="moon", size=20),
            value="dark",
        ),
        on_change=set_color_mode,
        variant="classic",
        radius="large",
        value=color_mode,
    )


def nav():
    return rx.box(
        rx.hstack(
            rx.link(
                "Python Zaragoza",
                href="/",
                font_weight="bold",
                font_size="1.25rem",
            ),
            rx.spacer(),
            rx.hstack(
                rx.link("Eventos", href="/events"),
                rx.link("Blog", href="/blog"),
                # rx.link("Comunidad", href="/comunity"),
                rx.link("Charlas", href="/talks"),
                rx.link("Sobre", href="/about"),
                rx.link("Contacto", href="/contact"),
                dark_mode_toggle(),
                spacing="4",
                display=["none", "flex"],
            ),
            # Mobile menu
            rx.box(
                rx.menu.root(
                    rx.menu.trigger(rx.button("Menú")),
                    rx.menu.content(
                        rx.menu.item("Eventos", on_click=[rx.redirect("/events")]),
                        rx.menu.item("Blog", on_click=[rx.redirect("/blog")]),
                        # rx.menu.item("Comunidad", on_click=[rx.redirect("/comunity")]),
                        rx.menu.item("Charlas", on_click=[rx.redirect("/talks")]),
                        rx.menu.item("Sobre", on_click=[rx.redirect("/about")]),
                        rx.menu.item("Contacto", on_click=[rx.redirect("/contact")]),
                        rx.box(dark_mode_toggle(), padding="8px"),
                    ),
                ),
                display=["inline-flex", "none"],
            ),
            width="100%",
            align="center",
        ),
        style={
            "position": "sticky",
            "top": 0,
            "z_index": 1000,
            "padding": "0.75rem 0",
            # Bordes y fondo según modo
            "border_bottom": rx.color_mode_cond(
                light="#eaeaea 1px solid", dark="#222 1px solid"
            ),
            "background": rx.color_mode_cond(light="#ffffffcc", dark="#0b0b0bcc"),
            "backdrop_filter": "saturate(180%) blur(8px)",
        },
    )


def footer():
    return rx.box(
        rx.vstack(
            rx.text("© 2025 PythonZgz · Comunidad Python en Zaragoza"),
            rx.hstack(
                rx.hstack(
                    rx.icon(tag="external-link", size=16),
                    rx.link(
                        "Telegram", href="https://t.me/python_zgz", is_external=True
                    ),
                    spacing="1",
                ),
                rx.text("·"),
                rx.hstack(
                    rx.icon(tag="external-link", size=16),
                    rx.link(
                        "Meetup",
                        href="https://www.meetup.com/es-ES/python_zgz/",
                        is_external=True,
                    ),
                    spacing="1",
                ),
                spacing="2",
                wrap="wrap",
                justify="center",
            ),
            spacing="2",
            align="center",
        ),
        style={
            "border_top": rx.color_mode_cond(
                light="#eaeaea 1px solid", dark="#222 1px solid"
            ),
            "padding": "1.25rem 0",
            "margin_top": "2rem",
            "background": rx.color_mode_cond(light="#fafafa", dark="#0b0b0b"),
        },
    )


def page_wrapper(*children):
    return rx.box(nav(), rx.box(*children, style=styles["container"]), footer())
