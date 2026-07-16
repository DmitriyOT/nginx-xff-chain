from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        xff = self.headers.get('X-Forwarded-For', 'NOT PRESENT')
        self.wfile.write(f'X-Forwarded-For: {xff}\n'.encode('utf-8'))

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), RequestHandler)
    print('App running on port 8080')
    server.serve_forever()
