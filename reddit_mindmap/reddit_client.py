from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import webbrowser

import praw


def init_reddit(config: dict) -> praw.Reddit:
    reddit_kwargs = {
        "client_id": config.get("client_id"),
        "client_secret": config.get("client_secret") or None,
        "user_agent": config.get("user_agent"),
    }
    if config.get("username") and config.get("password"):
        reddit_kwargs["username"] = config["username"]
        reddit_kwargs["password"] = config["password"]
    return praw.Reddit(**reddit_kwargs)


def oauth_authorize(reddit: praw.Reddit, scopes=None, redirect_port: int = 8080, timeout: int = 120) -> bool:
    """Run a local-browser OAuth flow without asking the user to paste tokens."""
    if scopes is None:
        scopes = ["identity", "read", "history"]

    state = "reddit_scraper_state"
    redirect_uri = f"http://localhost:{redirect_port}/authorize_callback"
    reddit.config.redirect_uri = redirect_uri
    auth_url = reddit.auth.url(scopes, state, "permanent")

    print("\nOpen this URL in your browser to authorize the application:")
    print(auth_url)
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    code_container = {"code": None}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            from urllib import parse

            params = dict(parse.parse_qsl(parse.urlparse(self.path).query))
            if params.get("state") == state and params.get("code"):
                code_container["code"] = params["code"]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authorization successful. You can close this window.</h1></body></html>")
                return
            self.send_response(400)
            self.end_headers()

        def log_message(self, format, *args):
            return

    try:
        server = HTTPServer(("localhost", redirect_port), Handler)
    except OSError as exc:
        print(f"Could not start local OAuth server on port {redirect_port}: {exc}")
        return False

    server.timeout = 1
    start = time.time()
    print(f"Listening on {redirect_uri} for redirect (timeout {timeout}s)...")
    while time.time() - start < timeout and code_container["code"] is None:
        server.handle_request()
    server.server_close()

    if not code_container["code"]:
        print("Authorization timed out or was cancelled")
        return False

    reddit.auth.authorize(code_container["code"])
    print("Authorization complete")
    return True
