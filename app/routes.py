from flask import Blueprint, jsonify, render_template
from datetime import datetime
from .scraper import fetch_trending_topics
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URI = os.getenv("MONGO_DB_URI")
client = pymongo.MongoClient(MONGO_DB_URI)
db = client["stir"]
collection = db["trending_topics"]

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

# Homepage to Display Trends
@scraper_bp.route('/', methods=['GET'])
def index():
    latest_trend = collection.find_one(sort=[("timestamp", -1)])  # Fetch latest trend
    return render_template('index.html', trend=latest_trend)
