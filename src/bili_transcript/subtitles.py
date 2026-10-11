"""抓取并解析 B 站字幕 JSON。"""

from . import api


def _normalize_url(u: str) -> str | None:
    if not u:
        return None
    if u.startswith("//"):
        u = "https:" + u
    return u


def fetch_subtitle(sub: dict) -> dict | None:
    """下载一条字幕并解析为 {lang, full_text, sentences}。

    sentences 中每条含 text / start(ms) / end(ms)，与 ASR 输出格式统一。
    """
    url = _normalize_url(sub.get("url"))
    if not url:
        return None
    r = api._session.get(
        url,
        headers={"User-Agent": api.config.USER_AGENT, "Referer": "https://www.bilibili.com"},
        timeout=30,
    )
    r.raise_for_status()
    j = r.json()
    body = j.get("body") or []
    sentences = []
    for seg in body:
        sentences.append(
            {
                "text": (seg.get("content") or "").strip(),
                "start": int(float(seg.get("from", 0)) * 1000),
                "end": int(float(seg.get("to", 0)) * 1000),
            }
        )
    full_text = "".join(s["text"] for s in sentences)
    return {"lang": sub.get("lan"), "full_text": full_text, "sentences": sentences}
