from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import dotenv_values
import http.client, urllib.parse
import json


# Load API keys and configuration from .env file
config = dotenv_values(".env")
app = Flask(__name__, static_folder='static')
CORS(app)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# MongoDB Connection Setup
client = MongoClient('mongodb://localhost:27017')
db = client['cricket']
users_collection = db['users']

# API Endpoints
LIVE_SCORE_API = config['LIVE_SCORE_API']
SERIES_API = config['SERIES_API']
MEDIASTACK_API_KEY = config['MEDIASTACK_API_KEY']

# Fetch data from an API
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return {}

# Fetch cricket news from Mediastack API
def fetch_news_api():
    conn = http.client.HTTPConnection('api.mediastack.com')
    params = urllib.parse.urlencode({
        'access_key': config['MEDIASTACK_API_KEY'],  # Use your actual API key from .env
        'categories': '-general,-sports',      # Exclude general and sports categories
        'keywords': 'cricket',                 # Filter for cricket-related news
        'sort': 'published_desc',
        'limit': 10                            # Limit results to 10 news items
    })
    
    try:
        conn.request('GET', f'/v1/news?{params}')
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        news_data = json.loads(data)
        return news_data.get('data', [])
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# Route: Homepage (Navbar)
@app.route('/')
def navbar():
    news_data = fetch_news_api()
    print("News data in navbar route:", news_data)  # Debug print
    return render_template('nav-bar.html', news_data=news_data)

# Route: User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

# Route: User Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash('Email already exists', 'error')
        else:
            hashed_password = generate_password_hash(password)
            users_collection.insert_one({'email': email, 'password': hashed_password})
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
    
    return render_template('signup.html')

# Route: User Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('navbar'))

# Route: Main Live Score Page
@app.route('/main')
def main():
    live_scores = fetch_data(LIVE_SCORE_API).get('data', [])
    
    scores = []
    for score in live_scores:
        team1 = score['teamInfo'][0]
        team2 = score['teamInfo'][1]
        team1_score = score['score'][0] if len(score['score']) > 0 else {}
        team2_score = score['score'][1] if len(score['score']) > 1 else {}

        scores.append({
            'match_name': score.get('name', ''),
            'match_type': score.get('matchType', ''),
            'status': score.get('status', ''),
            'venue': score.get('venue', ''),
            'date': score.get('date', ''),
            'team1': {
                'name': team1.get('name', ''),
                'shortname': team1.get('shortname', ''),
                'img': team1.get('img', ''),
                'score': f"{team1_score.get('r', 0)}/{team1_score.get('w', 0)} in {team1_score.get('o', 0)} overs" if team1_score else 'N/A'
            },
            'team2': {
                'name': team2.get('name', ''),
                'shortname': team2.get('shortname', ''),
                'img': team2.get('img', ''),
                'score': f"{team2_score.get('r', 0)}/{team2_score.get('w', 0)} in {team2_score.get('o', 0)} overs" if team2_score else 'N/A'
            }
        })
    
   

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
