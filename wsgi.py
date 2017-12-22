"""REST API prividing access to webserver resources for mobile agents."""

from app import app
if __name__ == "__main__":
    app.run(host='0.0.0.0')
