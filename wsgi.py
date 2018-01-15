"""Gunicorn entry point wrapping app creation."""

import os
from app import create_app

app_config_class = os.getenv('APP_SETTINGS')
app = create_app(app_config_class)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
