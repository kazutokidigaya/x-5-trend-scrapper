from flask import Flask
import os

def create_app():
    app = Flask(__name__, template_folder='../templates')  # Explicit path
    app.config['SECRET_KEY'] = 'supersecretkey'

    from .routes import scraper_bp
    app.register_blueprint(scraper_bp, url_prefix='/')

    return app
