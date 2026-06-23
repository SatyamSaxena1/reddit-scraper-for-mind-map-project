import getpass
import os


DEFAULT_CONFIG = {
    "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
    "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
    "user_agent": os.getenv("REDDIT_USER_AGENT", "MySavedPostsFetcher/1.0"),
    "username": os.getenv("REDDIT_USERNAME", ""),
    "password": os.getenv("REDDIT_PASSWORD", ""),
}


def interactive_config() -> dict[str, str]:
    print("Interactive setup for Reddit scraper")
    use_env = input("Use environment variables for Reddit credentials if present? [Y/n]: ").strip().lower()
    if use_env in {"", "y", "yes"}:
        return dict(DEFAULT_CONFIG)

    cfg = {
        "client_id": input(f"Reddit client_id [{DEFAULT_CONFIG['client_id']}]: ") or DEFAULT_CONFIG["client_id"],
        "client_secret": input(
            f"Reddit client_secret [{'hidden' if DEFAULT_CONFIG['client_secret'] else ''}]: "
        )
        or DEFAULT_CONFIG["client_secret"],
        "user_agent": input(f"user_agent [{DEFAULT_CONFIG['user_agent']}]: ") or DEFAULT_CONFIG["user_agent"],
        "username": "",
        "password": "",
    }
    want_auth = input("Provide Reddit username/password for private/age-gated content? [y/N]: ").strip().lower()
    if want_auth in {"y", "yes"}:
        cfg["username"] = input("username: ")
        cfg["password"] = getpass.getpass("password (hidden): ")
    return cfg
