from flask import Blueprint, jsonify
from datetime import datetime
from flask_cors import CORS
from .scraper import fetch_trending_topics

scraper_bp = Blueprint('scraper_bp', __name__)
CORS(scraper_bp)  # Enable CORS for all routes

# Route to Trigger Scraping (API Endpoint)
@scraper_bp.route('/scrape', methods=['GET'])
def scrape_trending():
    try:
        trends = fetch_trending_topics()
        return jsonify({
            "message": "Scraping completed successfully!",
            "trends": trends,
            "timestamp": str(datetime.now())
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
