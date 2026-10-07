"""命令行入口：解析链接 -> 取字幕或音频ASR -> 输出 Markdown。"""

import argparse
import json
import os
import sys

from . import api, asr, download, subtitles, utils


def _collect_subtitles(info, bvid, cid):
    """汇总 view 接口与 player 接口的字幕，去重。"""
    seen = set()
    out = []
    for s in list(info["subtitles"]) + api.get_player_subtitles(bvid, cid):
        url = s.get("url")
        if url and url not in seen:
            seen.add(url)
            out.append(s)
    # 中文优先
    out.sort(key=lambda s: 0 if (s.get("lan") or "").startswith("zh") else 1)
    return out


def run(args) -> int:
    corrections = {}
    if args.corrections and os.path.exists(args.corrections):
        with open(args.corrections, encoding="utf-8") as f:
            corrections = json.load(f)

    print(f"[1/5] 解析链接: {args.url}")
    bvid = api.resolve_bvid(args.url)
    print(f"      BV: {bvid}")

    print("[2/5] 获取视频信息...")
    info = api.get_video_info(bvid)
    cid = info["pages"][0]["cid"]
    print(
        f"      标题: {info['title']} | UP主: {info['owner']} | 时长: {info['duration']}s"
    )

    subs = _collect_subtitles(info, bvid, cid)
    print(f"      可用字幕: {len(subs)} 条")

    result = None
    source_label = ""

    if subs:
        sub = subs[0]
        print(f"[3/5] 下载字幕: {sub.get('lan_doc')} ({sub.get('lan')})")
        fetched = subtitles.fetch_subtitle(sub)
        if fetched and fetched["sentences"]:
            result = fetched
            source_label = f"字幕-{sub.get('lan_doc') or sub.get('lan')}"
    else:
        print("[3/5] 未检测到字幕，准备音频转写")
        if args.no_asr:
            print("      已指定 --no-asr，退出。")
            return 2

    if result is None:
        cookies = api.get_buvid_cookie()
        audio_url = api.get_audio_url(bvid, cid, cookies=cookies)
        if not audio_url:
            print("[错误] 无法获取音频地址（可能受地区/会员/登录限制）。")
            print("       可尝试设置环境变量 BILI_COOKIE 后重试。")
            return 3
        os.makedirs(args.workdir, exist_ok=True)
        raw_audio = os.path.join(args.workdir, "audio.m4s")
        wav = os.path.join(args.workdir, "audio.wav")
        print("[4/5] 下载音频并转码...")
        download.download_file(audio_url, raw_audio)
        download.convert_to_wav(raw_audio, wav)
        print("      语音识别中（首次运行会下载模型，请耐心等待）...")
        result = asr.transcribe(wav, device=args.device)
        source_label = "语音识别(ASR)"
        if not args.keep_audio:
            for tmp in (raw_audio, wav):
                try:
                    os.remove(tmp)
                except OSError:
                    pass

    print("[5/5] 生成文稿...")
    meta = {
        "title": info["title"],
        "owner": info["owner"],
        "duration_sec": info["duration"],
        "bvid": bvid,
        "url": args.url,
    }
    md = utils.build_markdown(
        meta, source_label, result["full_text"], result["sentences"], corrections=corrections
    )
    out = args.output or (info["title"] + ".md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"完成 -> {out}")
    return 0


def main():
    p = argparse.ArgumentParser(
        description="提取任意 B 站视频的字幕或讲稿（无字幕时自动语音识别）。"
    )
    p.add_argument("url", help="B站视频链接（b23.tv / BVxxxx / avxxxx）")
    p.add_argument("-o", "--output", default=None, help="输出 Markdown 路径，默认 <标题>.md")
    p.add_argument("--device", default="cpu", help="ASR 设备：cpu 或 cuda:0")
    p.add_argument(
        "--no-asr",
        action="store_true",
        help="仅尝试抓取字幕；无字幕时直接退出，不下载音频识别",
    )
    p.add_argument(
        "--corrections",
        default=None,
        help="可选的校对词典 JSON 路径（见 examples/corrections_demo.json）",
    )
    p.add_argument("--keep-audio", action="store_true", help="保留下载的音频临时文件")
    p.add_argument("--workdir", default=".", help="临时文件目录（默认当前目录）")
    args = p.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
