from flask import Flask, request, render_template, redirect, url_for
import requests

app = Flask(__name__)

def isSafe(url):
    blacklist={'127', 'local', '2130706433', '017700000001', '::1', '0.0.0.0', '[::]', 'ffff', '0.0.0.0', '0x', '..', '%2e%2e', '@'}
    return all([i not in url.lower() for i in blacklist])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url'] or ''
        if not isSafe(url): return 'Access denied. URL parameter included one or more of the blacklisted keywords.'
        return redirect(url_for('index', url=url))
    url = request.args.get('url') or ''
    if url: 
        desc = 'The admin will visit your URL.'
        try: req = 'Your response: ' + requests.get(url).text
        except: return 'Uh-oh... Try again!'
    else: req, desc = '', ''
    return render_template('index.html', q = req, desc=desc)

@app.route('/admin')
def js():
    if request.remote_addr != '127.0.0.1': return 'Access denied. Page only accessible from server side.'
    query = request.args.get("q", "")
    return query, 200, {'Content-Type': 'application/javascript'}

if __name__ == '__main__':
    app.run()
