"""Check GitHub releases for a newer version of Muslim Desk."""
from __future__ import annotations

GITHUB_API = "https://api.github.com/repos/Ahmedseko/muslim-desk/releases/latest"
RELEASES_URL = "https://github.com/Ahmedseko/muslim-desk/releases/latest"


def _ver(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.lstrip("v").split(".") if x.isdigit())


def check_for_update(current_version: str, timeout: int = 6) -> tuple[str, str] | None:
    """Return (latest_version, download_url) if a newer release exists, else None."""
    try:
        import requests
        r = requests.get(GITHUB_API, timeout=timeout,
                         headers={"Accept": "application/vnd.github+json"})
        if r.status_code != 200:
            return None
        data = r.json()
        tag = data.get("tag_name", "")
        if not tag:
            return None
        if _ver(tag) > _ver(current_version):
            url = data.get("html_url", RELEASES_URL)
            return tag.lstrip("v"), url
        return None
    except Exception:
        return None
