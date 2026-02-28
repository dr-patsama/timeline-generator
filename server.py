import os
import json
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

SAVED_TIMELINE_DIR = '/Users/drpat/Documents/เอกสารคนไข้/saved timeline'
TIMELINE_DIR = '/Users/drpat/Documents/เอกสารคนไข้/saved timeline'

# Ensure directories exist
os.makedirs(SAVED_TIMELINE_DIR, exist_ok=True)
os.makedirs(TIMELINE_DIR, exist_ok=True)

class TimelineServer(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/list':
            files = []
            try:
                for filename in os.listdir(SAVED_TIMELINE_DIR):
                    if filename.endswith(".json"):
                        filepath = os.path.join(SAVED_TIMELINE_DIR, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            try:
                                data = json.load(f)
                                files.append(data)
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                print(f"Error reading directory: {e}")
            
            # Sort by timestamp, most recent first
            files.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            self.wfile.write(json.dumps(files).encode('utf-8'))
        else:
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                file_type = data.get('type') # 'json', 'jpg', 'pdf'
                filename = data.get('filename')
                content = data.get('content')
                
                if file_type == 'json':
                    filepath = os.path.join(SAVED_TIMELINE_DIR, f"{filename}.json")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(content, ensure_ascii=False, indent=2))
                elif file_type == 'jpg':
                    filepath = os.path.join(TIMELINE_DIR, f"{filename}.jpg")
                    # content is expected to be base64 data url like 'data:image/jpeg;base64,...'
                    header, encoded = content.split(",", 1)
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(encoded))
                elif file_type == 'pdf':
                    filepath = os.path.join(TIMELINE_DIR, f"{filename}.pdf")
                    # content is expected to be base64 data url like 'data:application/pdf;base64,...'
                    # or datauristring
                    if "," in content:
                        header, encoded = content.split(",", 1)
                    else:
                        encoded = content
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(encoded))
                elif file_type == 'delete':
                     file_id = data.get('id')
                     # To delete a file, we need to find it by id in the JSON contents
                     for fname in os.listdir(SAVED_TIMELINE_DIR):
                         if fname.endswith(".json"):
                             fpath = os.path.join(SAVED_TIMELINE_DIR, fname)
                             with open(fpath, 'r', encoding='utf-8') as f:
                                 try:
                                     file_data = json.load(f)
                                     if file_data.get('id') == file_id:
                                         os.remove(fpath)
                                         break
                                 except Exception:
                                     pass

                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                print(f"Error saving: {e}")
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
             self.wfile.write(json.dumps({"status": "error", "message": "not found"}).encode('utf-8'))

if __name__ == '__main__':
    port = 8012
    server = HTTPServer(('localhost', port), TimelineServer)
    print(f"Server running on http://localhost:{port}")
    server.serve_forever()
