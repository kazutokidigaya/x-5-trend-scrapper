from flask import Flask, request, jsonify, redirect
import os

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config['SECRET_KEY'] = 'supersecretkey'

    # HTTPS Redirect in Production
    @app.before_request
    def enforce_https():
        if request.headers.get('X-Forwarded-Proto') == 'http':
            return redirect(request.url.replace("http://", "https://"))

    # Health Check Route
    @app.route('/')
    def health_check():
        return jsonify({"message": "Backend is up and running!"}), 200

    from .routes import scraper_bp
    app.register_blueprint(scraper_bp, url_prefix='/')

    return app
