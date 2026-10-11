"""下载音频并用 ffmpeg 转码为 16kHz 单声道 wav（ASR 最佳输入）。"""

import os
import subprocess


def download_file(url: str, out_path: str) -> None:
    """流式下载到本地文件。"""
    import requests

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.bilibili.com",
    }
    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)


def convert_to_wav(in_path: str, out_path: str, sr: int = 16000) -> None:
    """调用系统 ffmpeg 将任意音频容器转为 16k 单声道 wav。"""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        in_path,
        "-ar",
        str(sr),
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        out_path,
    ]
    # ffmpeg 输出较啰嗦，直接丢弃。
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(out_path):
        raise RuntimeError("ffmpeg 转码失败，请确认已安装 ffmpeg 且在 PATH 中。")
