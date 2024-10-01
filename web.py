from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
from dotenv import dotenv_values

config = dotenv_values(".env")
app = Flask(__name__, static_folder='static')
CORS(app)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017')
db = client['cricket']
users_collection = db['users']

# API Endpoints
LIVE_SCORE_API = config['LIVE_SCORE_API']
SERIES_API = config['SERIES_API']


def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return {}

def scrape_icc_news():
    try:
        url = "https://www.icc-cricket.com/news"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_items = soup.find_all('div', class_='news-card')
        
        news_data = []
        for item in news_items[:5]:  # Limit to 5 news items
            title = item.find('h3', class_='news-card__title').text.strip()
            date = item.find('time', class_='news-card__date').text.strip()
            link = 'https://www.icc-cricket.com' + item.find('a')['href']
            
            news_data.append({
                'title': title,
                'date': date,
                'link': link
            })
        
        print("Scraped news data:", news_data)  # Debug print
        return news_data
    except Exception as e:
        print(f"Error scraping ICC news: {e}")
        return []

@app.route('/')
def navbar():
    news_data = scrape_icc_news()
    print("News data in navbar route:", news_data)  # Debug print
    return render_template('nav-bar.html', news_data=news_data)

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

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('navbar'))

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
    
    news_data = scrape_icc_news()
    print("News data in main route:", news_data)  # Debug print
    return render_template('main.html', scores=scores, news_data=news_data)

if __name__ == '__main__':
    app.run(debug=True)