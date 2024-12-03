from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import dotenv_values
import http.client, urllib.parse
import json
from functools import wraps
from bson.objectid import ObjectId  # For handling MongoDB ObjectIds
import ssl
import boto3  # For Amazon Cognito
import logging
import re

# Load API keys and configuration from .env file
config = dotenv_values(".env")
app = Flask(__name__, static_folder='static')
CORS(app)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Amazon DocumentDB connection setup
# Replace these values with your actual DocumentDB connection details
DOCUMENTDB_CLUSTER_ENDPOINT = config['DOCUMENTDB_CLUSTER_ENDPOINT']
DOCUMENTDB_PORT = config['DOCUMENTDB_PORT']
DOCUMENTDB_USERNAME = config['DOCUMENTDB_USERNAME']
DOCUMENTDB_PASSWORD = config['DOCUMENTDB_PASSWORD']

# Full connection URI for Amazon DocumentDB
connection_uri = f"mongodb://{DOCUMENTDB_USERNAME}:{DOCUMENTDB_PASSWORD}@{DOCUMENTDB_CLUSTER_ENDPOINT}:{DOCUMENTDB_PORT}/?ssl=false&retryWrites=false"

# Path to the downloaded SSL certificate
ssl_cert_path = 'D:\CricketInfo\ssl.pem'  # Replace with actual path to your SSL PEM file

# MongoDB connection with SSL verification for DocumentDB
client = MongoClient(connection_uri)
db = client['cricket']  # Your database name
users_collection = db['users']

# API Endpoints
LIVE_SCORE_API = config['LIVE_SCORE_API']
MEDIASTACK_API_KEY = config['MEDIASTACK_API_KEY']

# Amazon Cognito Configuration
COGNITO_USER_POOL_ID = config['COGNITO_USER_POOL_ID']
COGNITO_CLIENT_ID = config['COGNITO_CLIENT_ID']
COGNITO_REGION = config['COGNITO_REGION']

# Boto3 client for Cognito
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger(__name__)

# Helper function to check if the user is authenticated (using Cognito tokens)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("You need to log in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Cognito User Registration (Signup)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['phone_number']

        # Validate phone number format
        phone_regex = re.compile(r'^\+[1-9]\d{1,14}$')
        if not phone_regex.match(phone_number):
            flash('Invalid phone number format. Please use the format +[country code][number] (e.g., +14155552671)', 'error')
            return render_template('signup.html')

        try:
            # Register the user in Cognito
            cognito_client.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'phone_number', 'Value': phone_number}
                ]
            )
            flash('Account created successfully! Please confirm your email.', 'success')
            return redirect(url_for('confirm_signup'))
        except cognito_client.exceptions.UsernameExistsException:
            flash('Email or username already exists', 'error')
        except cognito_client.exceptions.InvalidParameterException as e:
            if 'phone number format' in str(e).lower():
                flash('Invalid phone number format. Please use the format +[country code][number] (e.g., +14155552671)', 'error')
            else:
                flash(f'Invalid parameter: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('signup.html')

# Cognito Email Confirmation (After Signup)
@app.route('/confirm-signup', methods=['GET', 'POST'])
def confirm_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        code = request.form.get('code')

        if not username or not code:
            flash('Both username and confirmation code are required.', 'error')
            return render_template('confirm_signup.html')

        try:
            cognito_client.confirm_sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,
                ConfirmationCode=code
            )
            flash('Account confirmed successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except cognito_client.exceptions.ExpiredCodeException:
            flash('The confirmation code has expired. A new code has been sent to your email.', 'warning')
            try:
                cognito_client.resend_confirmation_code(
                    ClientId=COGNITO_CLIENT_ID,
                    Username=username
                )
            except Exception as resend_error:
                flash(f'Error resending code: {str(resend_error)}', 'error')
        except cognito_client.exceptions.CodeMismatchException:
            flash('Invalid confirmation code. Please try again.', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('confirm_signup.html')

@app.route('/resend-confirmation-code', methods=['POST'])
def resend_confirmation_code():
    username = request.form.get('username')
    
    if not username:
        flash('Username is required to resend the confirmation code.', 'error')
        return redirect(url_for('confirm_signup'))

    try:
        cognito_client.resend_confirmation_code(
            ClientId=COGNITO_CLIENT_ID,
            Username=username
        )
        flash('A new confirmation code has been sent to your email.', 'success')
    except Exception as e:
        flash(f'Error resending confirmation code: {str(e)}', 'error')
    return redirect(url_for('confirm_signup'))


# Cognito User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            response = cognito_client.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )

            logger.debug(f"Cognito response: {response}")

            if 'AuthenticationResult' in response:
                session['username'] = username
                session['tokens'] = response['AuthenticationResult']
                flash('Logged in successfully!', 'success')
                return redirect(url_for('subscription'))  # Redirect to subscription page
            else:
                flash('Unexpected response from authentication service', 'error')
                return render_template('login.html')

        except cognito_client.exceptions.NotAuthorizedException:
            flash('Invalid username or password', 'error')
        except cognito_client.exceptions.UserNotConfirmedException:
            flash('Please confirm your email before logging in.', 'error')
        except cognito_client.exceptions.UserNotFoundException:
            flash('User not found. Please check your username.', 'error')
        except cognito_client.exceptions.InvalidParameterException as e:
            flash(f'Invalid parameter: {str(e)}', 'error')
        except cognito_client.exceptions.TooManyRequestsException:
            flash('Too many attempts. Please try again later.', 'error')
        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')
            logger.exception("Detailed login error")

    return render_template('login.html')

# Logout user
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('tokens', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('navbar'))

@app.route('/subscription', methods=['GET', 'POST'])
@login_required
def subscription():
    if request.method == 'POST':
        subscription_type = request.form['subscription_type']
        # Here you would typically process the subscription,
        # e.g., update the user's subscription status in your database
        
        # For this example, we'll just set a session variable
        session['subscribed'] = True
        flash('Subscription successful!', 'success')
        return redirect(url_for('main'))
    
    return render_template('subscription.html')

# Subscription required for main page
@app.route('/main')
@login_required
def main():
    if not session.get('subscribed'):
        flash('Please subscribe to access this page.', 'warning')
        return redirect(url_for('subscription'))

    # Fetch live scores
    live_scores = fetch_data(LIVE_SCORE_API).get('data', [])

    # Fetch news
    news_data = fetch_news_api()

    # Process live scores
    scores = []
    for score in live_scores:
        team_info = score.get('teamInfo', [])
        score_info = score.get('score', [])

        team1 = team_info[0] if len(team_info) > 0 else {}
        team2 = team_info[1] if len(team_info) > 1 else {}
        team1_score = score_info[0] if len(score_info) > 0 else {}
        team2_score = score_info[1] if len(score_info) > 1 else {}

        scores.append({
            'match_name': score.get('name', 'Unknown Match'),
            'match_type': score.get('matchType', 'Unknown Type'),
            'status': score.get('status', 'Unknown Status'),
            'venue': score.get('venue', 'Unknown Venue'),
            'date': score.get('date', 'Unknown Date'),
            'team1': {
                'name': team1.get('name', 'Team 1'),
                'shortname': team1.get('shortname', 'T1'),
                'img': team1.get('img', ''),
                'score': f"{team1_score.get('r', 0)}/{team1_score.get('w', 0)} in {team1_score.get('o', 0)} overs" if team1_score else 'N/A'
            },
            'team2': {
                'name': team2.get('name', 'Team 2'),
                'shortname': team2.get('shortname', 'T2'),
                'img': team2.get('img', ''),
                'score': f"{team2_score.get('r', 0)}/{team2_score.get('w', 0)} in {team2_score.get('o', 0)} overs" if team2_score else 'N/A'
            }
        })
    
    # Fetch upcoming series (you'll need to implement this function)
    #series = fetch_upcoming_series()
    #series=series,

    return render_template('main.html', scores=scores, news_data=news_data,  username=session['username'])


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
        'access_key': MEDIASTACK_API_KEY,
        'keywords': 'cricket',
        'sort': 'published_desc',
        'limit': 20
    })
    
    try:
        conn.request('GET', f'/v1/news?{params}')
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        news_data = json.loads(data)
        logger.debug(f"Fetched news data: {news_data}")  # Add this line
        return news_data.get('data', [])
    except Exception as e:
        logger.error(f"Error fetching news: {e}")  # Change this to use logger
        return []

# Route: Homepage (Navbar)
@app.route('/')
def navbar():
    news_data = fetch_news_api()
    return render_template('nav-bar.html', news_data=news_data)

@app.route('/profile')
def profile():
    # Add your profile page logic here
    # You might want to check if user is logged in
    return render_template('profile.html')

@app.route('/settings')
def settings():
    # Add your settings page logic here
    # You might want to check if user is logged in
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)
