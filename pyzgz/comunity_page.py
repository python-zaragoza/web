import reflex as rx
from .layout import page_wrapper, styles


def comunity():
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Comunidad"),
                rx.text("Únete a nuestros canales:", text_align="center"),
                rx.list(
                    rx.list_item(
                        rx.link(
                            "Telegram", href="https://t.me/python_zgz", is_external=True
                        )
                    ),
                    rx.list_item(
                        rx.link(
                            "Meetup",
                            href="https://www.meetup.com/es-ES/python_zgz/",
                            is_external=True,
                        )
                    ),
                ),
                spacing="3",
                align="center",
            ),
            style=styles["section"],
        )
    )
