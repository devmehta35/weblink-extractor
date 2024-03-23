from flask import Flask, render_template, request
import time
from googlesearch import search

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form.get('query')
        start_time = time.monotonic()
        urls = [url for url in search(query)]
        end_time = time.monotonic()
        execution_time = end_time - start_time
        return render_template('results.html', urls=urls, execution_time=execution_time)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
