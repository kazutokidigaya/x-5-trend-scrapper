from flask import Blueprint, jsonify, render_template
from datetime import datetime
from .scraper import fetch_trending_topics

scraper_bp = Blueprint('scraper_bp', __name__)

# Route to Trigger Scraping
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

# Homepage to Render HTML
@scraper_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Health Check Route (Separate Path)
@scraper_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"message": "Backend is up and running!"})
