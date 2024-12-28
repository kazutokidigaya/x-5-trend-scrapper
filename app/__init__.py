from flask import Flask, request, jsonify, redirect
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'

    # Force HTTPS on Production
    @app.before_request
    def enforce_https():
        if request.headers.get('X-Forwarded-Proto') == 'http':
            return redirect(request.url.replace("http://", "https://"))

    # Health Check Route (API Only)
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"message": "Backend is up and running!"}), 200

    from .routes import scraper_bp
    app.register_blueprint(scraper_bp, url_prefix='/')

    return app
