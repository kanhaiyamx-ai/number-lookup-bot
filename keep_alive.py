from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

def run():
    server = HTTPServer(("0.0.0.0", 8080), BaseHTTPRequestHandler)
    server.serve_forever()

def keep_alive():
    t = threading.Thread(target=run)
    t.start()
