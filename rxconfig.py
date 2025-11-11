import reflex as rx

class AppConfig(rx.Config):
    app_name: str
    db_url: str = "sqlite:///pyzgz.db"

config = AppConfig(app_name="pyzgz")
