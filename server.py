"""
阿毛烧烤 · 厨房订单服务器
启动方式: python server.py
顾客端: http://你的IP:8080/amao-bbq-swipe.html
厨房屏: http://你的IP:8080/kitchen.html
"""
import json, os, time, re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ORDERS_FILE = 'orders.json'

def load_orders():
    if not os.path.exists(ORDERS_FILE): return []
    try:
        with open(ORDERS_FILE, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders[:200], f, ensure_ascii=False, indent=2)

def gen_order_no():
    orders = load_orders()
    today = time.strftime('%y%m%d')
    today_orders = [o for o in orders if o.get('no','').startswith(today)]
    seq = len(today_orders) + 1
    return f"{today}-{seq:03d}"

class Server(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/order':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            order = json.loads(body)
            order['no'] = gen_order_no()
            order['time'] = time.strftime('%H:%M:%S')
            order['status'] = 'new'
            orders = load_orders()
            orders.insert(0, order)
            save_orders(orders)
            self._json_response({'ok': True, 'no': order['no']})
        elif self.path.startswith('/order/'):
            # /order/<no>/cancel  or  /order/<no>/done
            parts = self.path.strip('/').split('/')
            if len(parts) >= 3:
                no = parts[1]
                action = parts[2]  # 'cancel' or 'done'
                orders = load_orders()
                for o in orders:
                    if o.get('no') == no:
                        o['status'] = 'cancelled' if action == 'cancel' else 'done'
                        save_orders(orders)
                        self._json_response({'ok': True, 'no': no, 'status': o['status']})
                        return
                self._json_response({'ok': False, 'error': 'not found'}, 404)
            else:
                self.send_response(404); self.end_headers()
        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

    def _json_response(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_GET(self):
        if self.path == '/orders':
            orders = load_orders()
            self._json_response(orders)
        elif self.path == '/orders/active':
            # Only new + done (hide cancelled)
            orders = [o for o in load_orders() if o.get('status') != 'cancelled']
            self._json_response(orders)
        elif self.path == '/kitchen':
            self.send_response(302)
            self.send_header('Location', '/kitchen.html')
            self.end_headers()
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        msg = format % args
        if '/orders' not in msg:
            safe = msg.encode('ascii', errors='replace').decode()
            print(f"  {safe}")

if __name__ == '__main__':
    import socket
    host = '0.0.0.0'
    port = 8080
    local_ip = socket.gethostbyname(socket.gethostname())
    print('=' * 50)
    print('  [Amao BBQ] Order Server Started')
    print('=' * 50)
    print(f'  Kitchen:  http://{local_ip}:8080/kitchen.html')
    print(f'  Customer: http://{local_ip}:8080/amao-bbq-swipe.html')
    print(f'  API:      http://{local_ip}:8080/orders')
    print('=' * 50)
    print('  Same WiFi -> scan QR code -> order!')
    print()
    HTTPServer((host, port), Server).serve_forever()
