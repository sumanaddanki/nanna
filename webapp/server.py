"""
Simple proxy server for Resemble API (to bypass CORS)
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.request
import urllib.error

# Resemble config
RESEMBLE_API_TOKEN = "DDAUBqxvIm3kToMoM8XCUgtt"
RESEMBLE_VOICE_UUID = "680d1fb7"
RESEMBLE_PROJECT_UUID = "f0a60a69"

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/resemble':
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            text = data.get('text', '')

            # Call Resemble API
            url = f"https://app.resemble.ai/api/v2/projects/{RESEMBLE_PROJECT_UUID}/clips"

            req_data = json.dumps({
                "body": text,
                "voice_uuid": RESEMBLE_VOICE_UUID,
                "is_public": False,
                "is_archived": False
            }).encode('utf-8')

            req = urllib.request.Request(url, data=req_data, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Token token={RESEMBLE_API_TOKEN}')

            try:
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode('utf-8'))

                    # Send response
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode('utf-8'))

            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

if __name__ == '__main__':
    port = 3333
    print(f"Starting server on http://localhost:{port}")
    print("With Resemble API proxy at /api/resemble")
    server = HTTPServer(('localhost', port), ProxyHandler)
    server.serve_forever()
