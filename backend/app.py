from serpapi import GoogleSearch
from flask import Flask, render_template, make_response, jsonify, request, Response
import requests
import json
import os
import time
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app)


def format_server_time():
  server_time = time.localtime()
  return time.strftime("%I:%M:%S %p", server_time)


@app.route('/')
def index():
    context = { 'server_time': format_server_time() }
    return jsonify(context)


@app.route('/api/gsearch/<query>')
def google_image_serp(query):
    # https://serpapi.com/search-api
    gsearch = GoogleSearch({
        "q": query, 
        "tbm": "isch",
        "gl": "us", "safe": "active",
        "api_key": "299af8d20c391660a53e49691eb092d7254e397db362d3d074f42d028d852c9b"
    })
    
    return jsonify(gsearch.get_dict())


@app.route('/api/karlo/<api_type>', methods=['POST'])
def karlo(api_type):
    KARLO_URL = f'https://api.kakaobrain.com/v1/inference/karlo-dev/{api_type}'

    data = json.loads(request.get_data())
    if data['prompt'].get('image', '').startswith('http'):
        data['prompt']['image'] = base64.b64encode(requests.get(data['prompt']['image']).content).decode('utf-8')
    elif data['prompt'].get('image', '').startswith('data:image'):
        data['prompt']['image'] = data['prompt']['image'].split(',')[1].strip()

    headers = dict([('Content-Type', 'application/json'), ('Authorization', 'Bearer 0d7663ed-254a-40cd-8021-8f786e068367')])
    resp = requests.request(np
        method=request.method,
        url=KARLO_URL,
        headers=headers,
        json=data,
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response


@app.route('/api/download', methods=['POST'])
def api_download():
    data = json.loads(request.get_data())
    return base64.b64encode(requests.get(data['url']).content).decode('utf-8')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))