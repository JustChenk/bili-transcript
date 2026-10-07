"""纯函数单元测试（无需联网）。运行：pytest tests/"""

from bili_transcript import utils


def test_ms_to_ts():
    assert utils.ms_to_ts(0) == "00:00"
    assert utils.ms_to_ts(50000) == "00:50"
    assert utils.ms_to_ts(799300) == "13:19"


def test_split_sentences():
    segs = utils.split_sentences("你好。世界！真的吗？")
    assert segs == ["你好。", "世界！", "真的吗？"]


def test_build_paragraphs():
    text = "。".join(["短句"] * 100) + "。"
    paras = utils.build_paragraphs(text, max_len=120)
    assert len(paras) > 1
    # 每段都含有标点
    assert all(p.endswith("。") for p in paras)


def test_apply_corrections_empty():
    assert utils.apply_corrections("原始文本", {}) == "原始文本"


def test_apply_corrections():
    corr = {"原始": "修正"}
    assert utils.apply_corrections("原始文本", corr) == "修正文本"
