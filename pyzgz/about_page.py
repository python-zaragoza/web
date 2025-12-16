import reflex as rx
from .layout import page_wrapper, styles


def about():
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Sobre Python Zaragoza"),
                rx.text(
                    "Comunidad abierta y sin ánimo de lucro.",
                    max_width="48rem",
                    align="center",
                ),
                rx.text(
                    "Promovemos Python en Zaragoza mediante eventos y recursos.",
                    max_width="48rem",
                    align="center",
                ),
                spacing="3",
                align="center",
            ),
            style=styles["section"],
        )
    )
