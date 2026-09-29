from http import cookies
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import base64
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import time
from urllib.parse import parse_qs, urlparse

from slh_admin_bot import get_bot_response


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
USERS_FILE = DATA_DIR / "admin_users.json"
CHATBOT_FILE = DATA_DIR / "chatbot_knowledge.json"
ASSETS_DIR = ROOT / "assets"
SESSIONS = {}
SESSION_TTL = 60 * 60 * 8
EDITABLE_PAGES = [
    "index.html",
    "accommodation.html",
    "dining.html",
    "experiences.html",
    "about.html",
    "contact.html",
    "booking.html",
    "privacy.html",
    "booking-terms.html",
    "house-rules.html",
]


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 180000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def ensure_data_files():
    DATA_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text(
            json.dumps(
                {
                    "users": [
                        {
                            "username": "admin",
                            "password": hash_password("SecretLakeHouse2026!"),
                            "role": "owner",
                            "created_at": int(time.time()),
                        }
                    ]
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    if not CHATBOT_FILE.exists():
        CHATBOT_FILE.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")


def verify_password(password, encoded):
    try:
        scheme, salt, digest = encoded.split("$", 2)
        if scheme != "pbkdf2_sha256":
            return False
        return hmac.compare_digest(hash_password(password, salt), encoded)
    except ValueError:
        return False


def read_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_page_name(name):
    name = Path(str(name)).name
    if name not in EDITABLE_PAGES:
        raise ValueError("That page is not editable from the admin panel.")
    return name


def safe_asset_name(name):
    name = Path(str(name)).name.strip()
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip(".-")
    if not name:
        name = f"upload-{int(time.time())}.jpg"
    if not re.search(r"\.(jpg|jpeg|png|webp|gif)$", name, re.I):
        raise ValueError("Please upload a JPG, PNG, WEBP, or GIF image.")
    return name


class SecretLakeHouseHandler(SimpleHTTPRequestHandler):
    def send_json(self, status, data, headers=None):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)

    def read_json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body or "{}")

    def current_user(self):
        jar = cookies.SimpleCookie()
        jar.load(self.headers.get("Cookie", ""))
        token = jar.get("slh_admin_session")
        if not token:
            return None
        session = SESSIONS.get(token.value)
        if not session or session["expires"] < time.time():
            SESSIONS.pop(token.value, None)
            return None
        session["expires"] = time.time() + SESSION_TTL
        return session["username"]

    def require_admin(self):
        username = self.current_user()
        if username:
            return username
        self.send_json(401, {"error": "Please log in first."})
        return None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/admin/"):
            self.handle_admin_get(parsed)
            return
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/chat":
            self.handle_chat()
            return
        if parsed.path.startswith("/api/admin/"):
            self.handle_admin_post(parsed)
            return
        self.send_error(404, "Not found")

    def handle_chat(self):
        try:
            data = self.read_json_body()
            message = str(data.get("message", ""))
            self.send_json(200, get_bot_response(message))
        except Exception as exc:
            self.send_json(
                200,
                {
                    "answer": "Secret Lake House is having trouble replying right now. Please contact us directly and we will help you.",
                    "needs_follow_up": True,
                    "error": str(exc),
                },
            )

    def handle_admin_get(self, parsed):
        if parsed.path == "/api/admin/session":
            username = self.current_user()
            self.send_json(200, {"authenticated": bool(username), "username": username})
            return

        username = self.require_admin()
        if not username:
            return

        if parsed.path == "/api/admin/users":
            users = read_json(USERS_FILE, {"users": []}).get("users", [])
            public_users = [{"username": user["username"], "role": user.get("role", "admin")} for user in users]
            self.send_json(200, {"users": public_users})
            return

        if parsed.path == "/api/admin/chatbot":
            self.send_json(200, read_json(CHATBOT_FILE, {"items": []}))
            return

        if parsed.path == "/api/admin/pages":
            self.send_json(200, {"pages": EDITABLE_PAGES})
            return

        if parsed.path == "/api/admin/menu":
            content = (ROOT / "index.html").read_text(encoding="utf-8")
            match = re.search(r'<div class="menu">(.*?)</div>', content, re.S)
            items = []
            if match:
                for href, label in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', match.group(1), re.S):
                    items.append({"label": re.sub(r"<[^>]+>", "", label).strip(), "href": href})
            self.send_json(200, {"items": items})
            return

        if parsed.path == "/api/admin/page":
            params = parse_qs(parsed.query)
            page = safe_page_name(params.get("file", [""])[0])
            self.send_json(200, {"file": page, "content": (ROOT / page).read_text(encoding="utf-8")})
            return

        if parsed.path == "/api/admin/assets":
            assets = sorted(f"assets/{path.name}" for path in ASSETS_DIR.iterdir() if path.is_file())
            self.send_json(200, {"assets": assets})
            return

        self.send_json(404, {"error": "Not found"})

    def handle_admin_post(self, parsed):
        try:
            if parsed.path == "/api/admin/login":
                data = self.read_json_body()
                username = str(data.get("username", "")).strip()
                password = str(data.get("password", ""))
                users = read_json(USERS_FILE, {"users": []}).get("users", [])
                match = next((user for user in users if user.get("username") == username), None)
                if not match or not verify_password(password, match.get("password", "")):
                    self.send_json(403, {"error": "Username or password is incorrect."})
                    return
                token = secrets.token_urlsafe(32)
                SESSIONS[token] = {"username": username, "expires": time.time() + SESSION_TTL}
                self.send_json(
                    200,
                    {"authenticated": True, "username": username},
                    {"Set-Cookie": f"slh_admin_session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age={SESSION_TTL}"},
                )
                return

            if parsed.path == "/api/admin/logout":
                jar = cookies.SimpleCookie()
                jar.load(self.headers.get("Cookie", ""))
                token = jar.get("slh_admin_session")
                if token:
                    SESSIONS.pop(token.value, None)
                self.send_json(200, {"ok": True}, {"Set-Cookie": "slh_admin_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"})
                return

            username = self.require_admin()
            if not username:
                return

            if parsed.path == "/api/admin/users":
                data = self.read_json_body()
                new_username = str(data.get("username", "")).strip()
                new_password = str(data.get("password", ""))
                role = str(data.get("role", "admin")).strip() or "admin"
                if not re.match(r"^[a-zA-Z0-9_.@-]{3,64}$", new_username):
                    self.send_json(400, {"error": "Username must be 3-64 letters, numbers, or . _ @ - characters."})
                    return
                if len(new_password) < 8:
                    self.send_json(400, {"error": "Password must be at least 8 characters."})
                    return
                store = read_json(USERS_FILE, {"users": []})
                users = store.setdefault("users", [])
                users[:] = [user for user in users if user.get("username") != new_username]
                users.append({"username": new_username, "password": hash_password(new_password), "role": role, "created_at": int(time.time())})
                write_json(USERS_FILE, store)
                self.send_json(200, {"ok": True})
                return

            if parsed.path == "/api/admin/users/delete":
                data = self.read_json_body()
                delete_username = str(data.get("username", "")).strip()
                store = read_json(USERS_FILE, {"users": []})
                users = store.setdefault("users", [])
                if delete_username == username:
                    self.send_json(400, {"error": "You cannot delete the account you are using right now."})
                    return
                if len(users) <= 1:
                    self.send_json(400, {"error": "At least one admin user is required."})
                    return
                store["users"] = [user for user in users if user.get("username") != delete_username]
                write_json(USERS_FILE, store)
                self.send_json(200, {"ok": True})
                return

            if parsed.path == "/api/admin/chatbot":
                data = self.read_json_body()
                items = data.get("items", [])
                if not isinstance(items, list):
                    self.send_json(400, {"error": "Chatbot items must be a list."})
                    return
                clean_items = []
                for item in items:
                    question = str(item.get("question", "")).strip()
                    keywords = str(item.get("keywords", "")).strip()
                    answer = str(item.get("answer", "")).strip()
                    if answer and (question or keywords):
                        clean_items.append({"question": question, "keywords": keywords, "answer": answer})
                write_json(CHATBOT_FILE, {"items": clean_items})
                self.send_json(200, {"ok": True, "items": clean_items})
                return

            if parsed.path == "/api/admin/page":
                data = self.read_json_body()
                page = safe_page_name(data.get("file", ""))
                content = str(data.get("content", ""))
                if "<html" not in content.lower() or "</html>" not in content.lower():
                    self.send_json(400, {"error": "This does not look like a complete HTML page."})
                    return
                (ROOT / page).write_text(content, encoding="utf-8")
                self.send_json(200, {"ok": True})
                return

            if parsed.path == "/api/admin/menu":
                data = self.read_json_body()
                items = data.get("items", [])
                if not isinstance(items, list) or not items:
                    self.send_json(400, {"error": "Add at least one menu item."})
                    return
                clean_items = []
                for item in items[:12]:
                    label = str(item.get("label", "")).strip()
                    href = str(item.get("href", "")).strip()
                    if not label or not href:
                        self.send_json(400, {"error": "Every menu item needs a label and link."})
                        return
                    if not re.match(r"^(?:[a-zA-Z0-9._/-]+|https?://[^\s]+)$", href):
                        self.send_json(400, {"error": f"Invalid menu link: {href}"})
                        return
                    clean_items.append({"label": label[:50], "href": href[:500]})

                updated = []
                for page in EDITABLE_PAGES:
                    target = ROOT / page
                    content = target.read_text(encoding="utf-8")
                    links = []
                    for item in clean_items:
                        active = ' class="active"' if item["href"] == page else ""
                        links.append(f'<a{active} href="{html.escape(item["href"], quote=True)}">{html.escape(item["label"])}</a>')
                    menu_html = '<div class="menu">' + ''.join(links) + '</div>'
                    revised, count = re.subn(r'<div class="menu">.*?</div>', menu_html, content, count=1, flags=re.S)
                    if count:
                        target.write_text(revised, encoding="utf-8")
                        updated.append(page)
                self.send_json(200, {"ok": True, "items": clean_items, "updated": updated})
                return

            if parsed.path == "/api/admin/upload":
                data = self.read_json_body()
                filename = safe_asset_name(data.get("filename", ""))
                data_url = str(data.get("dataUrl", ""))
                if "," not in data_url:
                    self.send_json(400, {"error": "Upload data is missing."})
                    return
                binary = base64.b64decode(data_url.split(",", 1)[1])
                if len(binary) > 8 * 1024 * 1024:
                    self.send_json(400, {"error": "Please keep image uploads under 8MB."})
                    return
                target = ASSETS_DIR / filename
                if target.exists():
                    target = ASSETS_DIR / f"{target.stem}-{int(time.time())}{target.suffix}"
                target.write_bytes(binary)
                self.send_json(200, {"ok": True, "path": f"assets/{target.name}"})
                return

            self.send_json(404, {"error": "Not found"})
        except Exception as exc:
            self.send_json(500, {"error": str(exc)})


ensure_data_files()
os.chdir(ROOT)
server = ThreadingHTTPServer(("127.0.0.1", 8091), SecretLakeHouseHandler)
print("Secret Lake House website preview: http://127.0.0.1:8091/")
print("Admin login: http://127.0.0.1:8091/admin.html")
server.serve_forever()
