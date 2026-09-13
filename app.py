import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ontology.catalog import CAPABILITIES, catalog_payload
from ontology.runtime import OntologyRuntime


ROOT = Path(__file__).parent
WEB = ROOT / "web"
runtime = OntologyRuntime()


class Handler(BaseHTTPRequestHandler):
    server_version = "OntologyMVP/1.0"

    def log_message(self, format, *args):
        print(f"[api] {self.address_string()} {format % args}")

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health": return self.send_json({"status": "ok", "mode": "mock", "service": "ontology-runtime"})
        if path == "/api/catalog": return self.send_json(catalog_payload())
        if path == "/api/reviews": return self.send_json(list(runtime.store.reviews.values()))
        if path == "/api/audits": return self.send_json(list(runtime.store.audits))
        if path == "/api/metrics": return self.send_json(runtime.store.metrics())
        if path.startswith("/api/sessions/"):
            session_id = path.rsplit("/", 1)[-1]
            return self.send_json(runtime.store.sessions.get(session_id, []))
        return self.serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            data = self.read_json()
            if path == "/api/intent/preview":
                query = data.get("message", "").strip()
                if not query: return self.send_json({"error": "message is required"}, 400)
                prediction = runtime.model.classify(query)
                intent = runtime.intents[prediction.intent_id]
                capability = CAPABILITIES[intent.capability_id]
                return self.send_json({"intent": prediction.to_dict(), "risk": intent.risk, "capability": {"id": capability.id, "name": capability.name}})
            if path == "/api/chat":
                if not data.get("message", "").strip(): return self.send_json({"error": "message is required"}, 400)
                result = runtime.handle_message(data.get("session_id", "demo"), data.get("user_id", "C1001"), data["message"].strip())
                return self.send_json(result)
            if path.startswith("/api/actions/") and path.endswith("/confirm"):
                action_id = path.split("/")[3]
                return self.send_json(runtime.confirm_action(action_id, data.get("actor", "C1001")))
            if path.startswith("/api/reviews/") and path.endswith("/decision"):
                review_id = path.split("/")[3]
                return self.send_json(runtime.decide_review(review_id, data.get("decision", "rejected"), data.get("actor", "agent-001"), data.get("note", "")))
            if path == "/api/config/publish":
                runtime.store.config_version += 1
                runtime.store.audit("config", "config.published", data.get("actor", "product-admin"), {"version": runtime.store.config_version, "change": data.get("change", "演示配置发布")})
                return self.send_json({"status": "published", "version": runtime.store.config_version})
            return self.send_json({"error": "not found"}, 404)
        except KeyError as exc:
            return self.send_json({"error": str(exc)}, 404)
        except Exception as exc:
            return self.send_json({"error": str(exc)}, 500)

    def serve_static(self, path):
        relative = "index.html" if path in ("/", "") else path.lstrip("/")
        target = (WEB / relative).resolve()
        if WEB.resolve() not in target.parents and target != WEB.resolve(): return self.send_json({"error": "forbidden"}, 403)
        if not target.exists() or not target.is_file():
            target = WEB / "index.html"
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    address = (os.getenv("APP_HOST", "127.0.0.1"), int(os.getenv("APP_PORT", "8000")))
    print(f"Automotive Ontology MVP running at http://{address[0]}:{address[1]}")
    ThreadingHTTPServer(address, Handler).serve_forever()
