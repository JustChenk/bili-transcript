"""文本与文档工具：时间戳格式化、断句分段、校对、Markdown 生成。"""

import re


def ms_to_ts(ms: int) -> str:
    """毫秒 -> mm:ss。"""
    sec = ms / 1000.0
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"


def apply_corrections(text: str, corrections: dict) -> str:
    """按词典替换明显的同音识别错误。空词典则不改动。"""
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text


def split_sentences(text: str) -> list:
    """按句末标点切句（保留标点）。"""
    parts = re.split(r"(?<=[。！？])", text)
    return [p for p in parts if p.strip()]


def build_paragraphs(text: str, max_len: int = 120) -> list:
    """把长文本按句聚合成若干段落，便于通读。"""
    segs = split_sentences(text)
    paras, cur = [], ""
    for seg in segs:
        cur += seg
        if len(cur) > max_len:
            paras.append(cur.strip())
            cur = ""
    if cur.strip():
        paras.append(cur.strip())
    return paras


def build_markdown(
    meta: dict,
    source_label: str,
    full_text: str,
    sentences: list,
    corrections: dict = None,
    paragraphs: list = None,
) -> str:
    """生成最终 Markdown 文稿（含段落版 + 时间戳版）。"""
    corrections = corrections or {}
    full_text = apply_corrections(full_text, corrections)
    sentences = [
        {**s, "text": apply_corrections(s["text"], corrections)} for s in sentences
    ]
    paras = paragraphs if paragraphs is not None else build_paragraphs(full_text)

    lines = []
    lines.append(f"# {meta['title']}（{source_label}）")
    lines.append("")
    lines.append("> **来源**：" + (meta.get("url") or ""))
    lines.append(f"> **UP主**：{meta.get('owner')}")
    lines.append(f"> **时长**：约 {meta.get('duration_sec')} 秒")
    lines.append(f"> **BV**：{meta.get('bvid')}")
    lines.append(
        "> **说明**：本文稿由 bili-transcript 自动生成；"
        "语音识别结果可能存在个别同音错误，引用时建议以视频原声核对。"
    )
    lines.append("")
    lines.append("---\n")
    lines.append("## 一、段落版\n")
    lines.append("\n\n".join(paras))
    lines.append("\n\n---\n")
    lines.append("## 二、时间戳版（[mm:ss]）\n")
    for s in sentences:
        t = s["text"].strip()
        if not t:
            continue
        lines.append(f"[{ms_to_ts(s['start'])}] {t}")
    return "\n".join(lines) + "\n"
