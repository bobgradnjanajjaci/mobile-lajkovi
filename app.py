from flask import Flask, request, render_template_string
from urllib.parse import urlparse
import requests

app = Flask(__name__)

# ======================
# CONFIG
# ======================
PANEL_URL = "https://godofpanel.com/api/v2
API_KEY = "c4868df4a78299b800d222cd9478ba17"
SERVICE_ID = 5836  # TikTok Comment Likes (DIRECT COMMENT LINK)

# ======================
# HTML
# ======================
HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>TikTok Comment Likes Fast Sender</title>
  <style>
    body { background:#0f172a; color:#e5e7eb; font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding:30px; }
    .container { max-width: 900px; margin: 0 auto; }
    textarea { width:100%; height:350px; background:#020617; color:#86efac; padding:15px; border:1px solid #334155; border-radius:8px; font-family:monospace; font-size: 14px; outline: none; }
    textarea:focus { border-color: #22c55e; }
    button { margin-top:15px; padding:15px 30px; font-size:16px; font-weight:bold; background:#22c55e; color:#0f172a; border:none; border-radius:6px; cursor:pointer; width: 100%; transition: 0.3s; }
    button:hover { background:#16a34a; transform: translateY(-2px); }
    pre { background:#020617; padding:16px; margin-top:20px; border-radius:8px; white-space:pre-wrap; line-height:1.6; border-left: 4px solid #3b82f6; }
    .success { color:#4ade80; font-weight: bold; }
    .error { color:#f87171; font-weight: bold; }
    .info { color:#60a5fa; }
    h2 { margin-bottom: 5px; }
    p { color: #94a3b8; margin-bottom: 20px; }
  </style>
</head>
<body>
<div class="container">
  <h2>🚀 TikTok Comment Likes (Simple Mode)</h2>
  <p>Format unosa: <code>LINK_KOMENTARA KOLIČINA</code> (npr. Zalijepi link i razmak pa broj)</p>
  
  <form method="post">
    <textarea name="orders" placeholder="https://www.tiktok.com/@user/video/123456... 100
https://vm.tiktok.com/ZMM... 250"></textarea>
    <button type="submit">POŠALJI NA PANEL</button>
  </form>

  {% if log %}
  <pre>{{ log }}</pre>
  {% endif %}
</div>
</body>
</html>
"""

def is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except:
        return False

def send_order(comment_url: str, quantity: int):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": comment_url,   # Direktan link komentara
        "quantity": quantity
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=20)
        response = r.json()

        if response.get("status") == "success":
            order_id = response.get("order", "N/A")
            return f'<span class="success">[OK] Order #{order_id} | {quantity} likes → Link: {comment_url[:50]}...</span>'
        else:
            error = response.get("error", str(response))
            return f'<span class="error">[ERROR] {error}</span>'

    except Exception as e:
        return f'<span class="error">[EXCEPTION] {str(e)}</span>'

@app.route("/", methods=["GET", "POST"])
def index():
    log_lines = []

    if request.method == "POST":
        raw = request.form.get("orders", "").strip()

        if not raw:
            log_lines.append('<span class="error">[SISTEM] Polje je prazno!</span>')
        else:
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            log_lines.append(f'<span class="info">[SISTEM] Procesuiram {len(lines)} linkova...</span>\n')

            for i, line in enumerate(lines, 1):
                # Splitamo samo na dva dijela: link i količina
                parts = line.rsplit(maxsplit=1) 
                
                if len(parts) < 2:
                    log_lines.append(f'[SKIP] #{i} Nedostaje količina → {line}')
                    continue

                comment_link, qty_raw = parts

                if not is_valid_url(comment_link):
                    log_lines.append(f'[SKIP] #{i} Neispravan URL → {comment_link}')
                    continue

                try:
                    qty = int(qty_raw)
                    if qty < 1: raise ValueError
                except:
                    log_lines.append(f'[SKIP] #{i} Neispravna količina → {qty_raw}')
                    continue

                # Slanje na panel
                result = send_order(comment_link, qty)
                log_lines.append(result)

    return render_template_string(HTML, log="\n".join(log_lines))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
