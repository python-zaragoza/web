import reflex as rx
from .layout import page_wrapper, styles, EMAIL


GOOGLE_FORM_URL = "https://forms.gle/qvMCiq8GkyCty79N8"


def talks():
    """Talk proposal via Google Forms (with optional email alternative)."""
    return page_wrapper(
        rx.section(
            rx.vstack(
                rx.heading("Propón una charla"),
                rx.text("Envíanos tu propuesta a través de nuestro formulario:"),
                rx.link(
                    rx.button("Abrir formulario de Charlas", variant="solid"),
                    href=GOOGLE_FORM_URL,
                    is_external=True,
                ),
                rx.text("Como alternativa, puedes escribirnos a:"),
                rx.link(EMAIL, href=f"mailto:{EMAIL}", is_external=True),
                spacing="4",
                align="center",
            ),
            style=styles["section"],
        )
    )


# Alternative version using Formspree (supports PDF upload)
# FORMSPREE_TALKS_ENDPOINT = "https://formspree.io/f/xzznqalo"


# def talks_formspree():
#     """Talk proposal via Formspree (supports PDF upload)."""
#     form_html = f'''
#     <form action="{FORMSPREE_TALKS_ENDPOINT}" method="POST" enctype="multipart/form-data">
#       <div style="display:flex; flex-direction:column; gap:12px; max-width:42rem; width:100%">
#         <input type="text" name="title" placeholder="Título de la charla" required />
#         <input type="text" name="speaker" placeholder="Ponente (tu nombre)" required />
#         <input type="email" name="email" placeholder="Email de contacto" required />
#         <input type="text" name="level" placeholder="Nivel (intro, intermedio, avanzado)" required />
#         <input type="number" name="duration" placeholder="Duración (minutos)" min="1" />
#         <input type="text" name="summary" placeholder="Resumen" required />
#         <textarea name="mensaje" rows="6" placeholder="Mensaje"></textarea>
#         <label>Adjunta PDF (opcional): <input type="file" name="attachment" accept="application/pdf" /></label>
#         <button type="submit">Enviar</button>
#       </div>
#     </form>
#     <p style="margin-top: 8px; font-size: 0.9rem; color: #555;">Si lo prefieres, envíanos un email a <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
#     '''

#     return page_wrapper(
#         rx.section(
#             rx.vstack(
#                 rx.heading("Propón una charla"),
#                 rx.text("Rellena el formulario o envíanos un email. Las propuestas se envían a través de Formspree."),
#                 rx.html(form_html),
#                 spacing="4",
#                 align="center",
#             ),
#             style=styles["section"],
#         )
#     )
