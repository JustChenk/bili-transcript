"""与 B 站公开 API 交互：链接解析、视频信息、字幕列表、音频直链。

说明：
- 公开 UGC 视频通常无需登录即可访问。若遇到 412/地区限制，可设置环境变量
  BILI_COOKIE（从浏览器开发者工具复制的 Cookie 字符串）后重试。
- 解析短链 b23.tv 时跟随重定向拿到真实页面地址。
"""

import os
import re

import requests

from . import config

_session = requests.Session()
_session.headers.update(config.HEADERS)


def _parse_cookie(cookie_str: str) -> dict:
    cookies = {}
    for pair in (cookie_str or "").split(";"):
        pair = pair.strip()
        if not pair or "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        cookies[k.strip()] = v.strip()
    return cookies


# 若环境变量提供了 Cookie，则所有请求自动带上（用于受限视频）。
_extra_cookies = _parse_cookie(os.environ.get("BILI_COOKIE", ""))
if _extra_cookies:
    _session.cookies.update(_extra_cookies)


def _get_json(url, params=None, cookies=None):
    r = _session.get(url, params=params, cookies=cookies, timeout=30)
    r.raise_for_status()
    return r.json()


def resolve_bvid(url: str) -> str:
    """从 b23.tv / BVxxxx / avxxxx 链接中解析出 BV 号。"""
    if "b23.tv" in url:
        r = _session.get(url, allow_redirects=True, timeout=30)
        url = r.url
    m = re.search(r"BV[0-9A-Za-z]+", url)
    if m:
        return m.group(0)
    m = re.search(r"av(\d+)", url, re.I)
    if m:
        data = _get_json(config.API_VIEW, params={"aid": m.group(1)})
        return data["data"]["bvid"]
    raise ValueError(f"无法从链接中解析出 BV 号: {url}")


def get_buvid_cookie() -> dict:
    """向 finger 接口换取一个 buvid3 cookie，用于绕过部分 412 限制。"""
    try:
        data = _get_json(config.API_FINGER)
        b3 = data.get("data", {}).get("b_3") or data.get("data", {}).get("buvid")
        if b3:
            return {"buvid3": b3}
    except Exception:
        pass
    return {}


def get_video_info(bvid: str) -> dict:
    """返回视频标题、UP主、时长、分P(cid) 与上传字幕列表。"""
    data = _get_json(config.API_VIEW, params={"bvid": bvid})["data"]
    pages = [
        {"page": p["page"], "cid": p["cid"], "duration": p.get("duration", 0)}
        for p in data["pages"]
    ]
    subs = []
    for s in data.get("subtitle", {}).get("list", []):
        subs.append(
            {"lan": s.get("lan"), "lan_doc": s.get("lan_doc"), "url": s.get("subtitle_url")}
        )
    return {
        "bvid": bvid,
        "title": data.get("title"),
        "owner": data.get("owner", {}).get("name"),
        "duration": data.get("duration", 0),
        "pubdate": data.get("pubdate"),
        "pages": pages,
        "subtitles": subs,
    }


def get_player_subtitles(bvid: str, cid: int) -> list:
    """从播放器接口拿字幕列表（AI 自动字幕往往在这里，不在 view 接口）。"""
    data = _get_json(config.API_PLAYER, params={"bvid": bvid, "cid": cid})["data"]
    subs = []
    for s in data.get("subtitle", {}).get("subtitles", []):
        subs.append(
            {"lan": s.get("lan"), "lan_doc": s.get("lan_doc"), "url": s.get("subtitle_url")}
        )
    return subs


def get_audio_url(bvid: str, cid: int, cookies: dict = None) -> str | None:
    """获取最佳音轨直链（DASH 或 FLV）。失败返回 None。"""
    params = {"bvid": bvid, "cid": cid, "qn": 64, "fnval": 16, "fourk": 1}
    data = _get_json(config.API_PLAYURL, params=params, cookies=cookies)
    if data.get("code") != 0:
        return None
    dash = data["data"].get("dash") or {}
    audios = dash.get("audio") or []
    if audios:
        best = max(audios, key=lambda x: x.get("bandwidth", 0))
        return best.get("baseUrl")
    durl = data["data"].get("durl")  # FLV 兜底
    if durl:
        return durl[0].get("url")
    return None
