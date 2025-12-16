import reflex as rx
from .layout import page_wrapper, styles


def blog():
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Blog"),
                rx.text(
                    "Notas de charlas, tutoriales y crónicas.", text_align="center"
                ),
                spacing="3",
                align="center",
            ),
            style=styles["section"],
        )
    )
