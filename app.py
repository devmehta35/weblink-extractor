from flask import Flask, render_template, request
from threading import Thread
import time
import uuid
from googlesearch import search
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

from flask_sslify import SSLify

# Load environment variables from the .env file
load_dotenv()

# Setup MongoDB Atlas connection
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri)
db = client['user_data']
collection = db['searches']

app = Flask(__name__)
sslify = SSLify(app) # To automatically Turn HTTP in HTTPS
results = {}

def background_search(query, id, ip_address):
    print(f"Starting search for query: {query}") # User's Query
    print(f"IP Address: {ip_address}") # User's IP Address
    start_time = time.monotonic()
    urls = []
    for url in search(query):
        urls.append(url)
        time.sleep(2)  # Add a delay of 1 second between requests
    print(f"Search completed. Found {len(urls)} results.") # Number of numbers
    for item in urls:
        index = urls.index(item)
        print(f"Link {index}: {item}") # Links from response
    end_time = time.monotonic()
    execution_time = round(end_time - start_time, 2)  # Round off to 2 decimal places
    results[id] = (urls, execution_time)

    # Store the data in MongoDB
    collection.insert_one({'ip': ip_address, 'query': query, 'num_results': len(urls), 'uuid': id, 'execution_time': execution_time, 'timestamp': datetime.now(), 'urls': urls})

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.headers.getlist("X-Forwarded-For"):
        user_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        user_ip = request.remote_addr
    if request.method == 'POST':
        query = request.form.get('query')
        id = str(uuid.uuid4())
        Thread(target=background_search, args=(query, id, user_ip)).start()
        return render_template('loading.html', id=id)
    return render_template('index.html')

@app.route('/results/<id>')
def results_page(id):
    if id in results:
        urls, execution_time = results[id]
        return render_template('results.html', urls=urls, execution_time=execution_time, num_results=len(urls))
    return "Results not ready, please refresh the page."

# Driver's Code
# if __name__ == '__main__':
#     app.run(debug=False)