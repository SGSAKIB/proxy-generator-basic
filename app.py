from flask import Flask, render_template, request, jsonify, send_file
import asyncio
from proxy_fetcher import fetch_all_sources, filter_working_proxies
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    all_proxies = fetch_all_sources()
    ok = asyncio.run(filter_working_proxies(all_proxies[:300]))
    return jsonify({
        'total_found': len(all_proxies),
        'working_count': len(ok),
        'working': ok,
    })

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json() or {}
    proxies = data.get('proxies', [])
    buf = io.BytesIO("\n".join(proxies).encode('utf-8'))
    buf.seek(0)
    return send_file(buf, mimetype='text/plain', as_attachment=True, download_name='working_proxies.txt')

if __name__ == '__main__':
    app.run(debug=True)
