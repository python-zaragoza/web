import reflex as rx
from .layout import page_wrapper, styles, EMAIL


def contact():
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Contacto"),
                rx.text("Para cualquier consulta o propuesta:"),
                rx.link(EMAIL, href=f"mailto:{EMAIL}", is_external=True),
                spacing="4",
                align="center",
            ),
            style=styles["section"],
        )
    )
