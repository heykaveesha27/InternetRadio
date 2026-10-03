from flask import Flask, Response
import requests

app = Flask(__name__)
STREAM_URL = "https://cp11.serverse.com/proxy/nethfm/stream"

@app.route('/stream')
def proxy_stream():
    # Force the radio server to send the ICY metadata
    req = requests.get(STREAM_URL, stream=True, headers={'Icy-MetaData': '1'})
    
    # Filter and grab the headers
    forwarded_headers = {k: v for k, v in req.headers.items() if k.lower().startswith('icy')}
    forwarded_headers['content-type'] = req.headers.get('content-type',"")

    # Print the headers to your terminal for debugging
    print(f"Forwarding these headers to ESP32: {forwarded_headers}")

    return Response(req.iter_content(chunk_size=1024), 
                    headers=forwarded_headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)