"""常量与默认配置。"""

# 浏览器 UA 与 Referer：B 站接口对请求头较敏感，保持为桌面端浏览器。
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Referer": "https://www.bilibili.com",
}

# B 站公开 Web API（无需登录即可访问绝大多数公开视频）。
API_VIEW = "https://api.bilibili.com/x/web-interface/view"
API_PLAYER = "https://api.bilibili.com/x/player/wbi/v2"
API_PLAYURL = "https://api.bilibili.com/x/player/playurl"
API_FINGER = "https://api.bilibili.com/x/frontend/finger/spi"

# FunASR 模型（首次运行会从 ModelScope 自动下载，约 1GB）。
ASR_MODEL = "paraformer-zh"
ASR_MODEL_REV = "v2.0.4"
VAD_MODEL = "fsmn-vad"
VAD_MODEL_REV = "v2.0.4"
PUNC_MODEL = "ct-punc"
PUNC_MODEL_REV = "v2.0.4"
