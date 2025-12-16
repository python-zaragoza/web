import reflex as rx
from .layout import page_wrapper, styles


def index():
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.image(
                    src="/logo.png", alt="Logo PythonZgz", width="200px", height="auto"
                ),
                rx.heading("Comunidad Python Zaragoza", size="8"),
                # rx.text(
                #     "Charlas, talleres y quedadas para aprender y compartir Python en Zaragoza.",
                #     text_align="center",
                #     max_width="40rem",
                # ),
                rx.hstack(
                    rx.link(rx.button("Próximos eventos"), href="/events"),
                    rx.link(
                        rx.button("Propón una charla", variant="outline"), href="/talks"
                    ),
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
