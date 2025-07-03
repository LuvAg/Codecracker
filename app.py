from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

# Set up Flask app with correct static folder
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'build'), static_url_path='')
CORS(app)

# -------------------- Codeforces --------------------
@app.route('/api/codeforces/<handle>')
def codeforces_data(handle):
    url = f'https://codeforces.com/api/user.info?handles={handle}'
    try:
        r = requests.get(url)
        data = r.json()
        if data['status'] == 'OK':
            user = data['result'][0]
            return jsonify({
                'status': 'OK',
                'result': {
                    'handle': user.get('handle'),
                    'rating': user.get('rating'),
                    'maxRating': user.get('maxRating'),
                    'rank': user.get('rank')
                }
            })
        else:
            return jsonify({'status': 'FAILED', 'message': 'User not found'})
    except Exception as e:
        return jsonify({'status': 'FAILED', 'message': 'Error fetching data', 'error': str(e)})

# -------------------- LeetCode --------------------
@app.route('/api/leetcode/<handle>')
def leetcode_data(handle):
    url = f'https://leetcode-stats-api.herokuapp.com/{handle}'
    try:
        r = requests.get(url)
        data = r.json()
        if 'status' in data and data['status'] == 'error':
            return jsonify({'status': 'FAILED', 'message': 'User not found'})
        return jsonify({
            'status': 'OK',
            'result': {
                'handle': handle,
                'rating': data.get('totalSolved'),
                'maxRating': None,
                'rank': data.get('ranking'),
                'totalEasy': data.get('easySolved'),
                'totalMedium': data.get('mediumSolved'),
                'totalHard': data.get('hardSolved')
            }
        })
    except Exception as e:
        return jsonify({'status': 'FAILED', 'message': 'Error fetching data', 'error': str(e)})

# -------------------- CodeChef --------------------
@app.route('/api/codechef/<handle>')
def codechef_data(handle):
    url = f'https://www.codechef.com/users/{handle}'
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return jsonify({'status': 'FAILED', 'message': 'User not found'})
        soup = BeautifulSoup(r.text, 'html.parser')
        rating_elem = soup.find('div', class_='rating-number')
        rating = rating_elem.text.strip() if rating_elem else 'N/A'
        ranks = soup.find('div', class_='rating-ranks')
        global_rank = 'N/A'
        if ranks:
            rank_links = ranks.find_all('a')
            if rank_links:
                global_rank = rank_links[0].text.strip()
        return jsonify({
            'status': 'OK',
            'result': {
                'handle': handle,
                'rating': rating,
                'maxRating': None,
                'rank': global_rank
            }
        })
    except Exception as e:
        return jsonify({'status': 'FAILED', 'message': 'Error parsing CodeChef profile', 'error': str(e)})

# -------------------- Serve React --------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# -------------------- Run --------------------
if __name__ == '__main__':
    app.run(debug=True)
#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass