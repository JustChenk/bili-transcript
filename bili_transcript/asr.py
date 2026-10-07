"""使用 FunASR 做中文语音识别（paraformer-zh + fsmn-vad + ct-punc）。

首次运行会从 ModelScope 自动下载模型（约 1GB），请保持网络畅通。
"""

from . import config


def transcribe(wav_path: str, device: str = "cpu") -> dict:
    """对 wav 做长音频转写，返回 {full_text, sentences}。

    sentences 中每条含 text / start(ms) / end(ms)。
    """
    from funasr import AutoModel

    model = AutoModel(
        model=config.ASR_MODEL,
        model_revision=config.ASR_MODEL_REV,
        vad_model=config.VAD_MODEL,
        vad_model_revision=config.VAD_MODEL_REV,
        punc_model=config.PUNC_MODEL,
        punc_model_revision=config.PUNC_MODEL_REV,
        disable_update=True,
        device=device,
        ncpu=4,
    )
    res = model.generate(
        input=wav_path,
        batch_size_s=300,  # 长音频按 300s 分批
        sentence_timestamp=True,  # 输出句子级时间戳
        return_spk_res=False,
    )
    item = res[0]
    full_text = item.get("text", "")

    sentences = []
    for s in item.get("sentence_info", []):
        t = (s.get("text") or "").strip()
        if not t:
            continue
        sentences.append(
            {"text": t, "start": int(s.get("start", 0)), "end": int(s.get("end", 0))}
        )
    return {"full_text": full_text, "sentences": sentences}
