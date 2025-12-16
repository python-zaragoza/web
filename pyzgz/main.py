import reflex as rx
from .index_page import index as index_page
from .events_page import events as events_page
from .blog_page import blog as blog_page
from .talks_page import talks as talks_page
from .about_page import about as about_page
from .contact_page import contact as contact_page

# ---------- App & routes ----------
app = rx.App(theme=rx.theme(appearance="dark"))
app.add_page(index_page, route="/", title="PythonZgz — Comunidad Python Zaragoza")
app.add_page(events_page, route="/events", title="Eventos · PythonZgz")
app.add_page(blog_page, route="/blog", title="Blog · PythonZgz")
# app.add_page(comunity_page, route="/comunity", title="Comunidad · PythonZgz")
app.add_page(talks_page, route="/talks", title="Proponer charla · PythonZgz")
app.add_page(about_page, route="/about", title="Sobre · PythonZgz")
app.add_page(contact_page, route="/contact", title="Contacto · PythonZgz")
