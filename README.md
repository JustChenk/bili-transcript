# bili-transcript

> 提取**任意 B 站视频**的字幕或讲稿：优先抓取官方/AI 字幕（快且准），没有字幕时自动下载音频并用中文语音识别（ASR）转写。

适合用来：扒演讲/口播类视频的逐字稿、做内容研究、给无字幕视频补字幕等。

---

## 功能特性

- ✅ **自动优先取字幕**：同时检查「上传字幕」与「AI 自动字幕」，有就用，零成本且最准确。
- ✅ **无字幕自动 ASR**：通过 B 站播放接口拿到音轨 → ffmpeg 转码 → FunASR（paraformer-zh + fsmn-vad + ct-punc）中文识别并自动加标点、时间戳。
- ✅ **输出 Markdown**：含「段落版」+「时间戳版 [mm:ss]」，直接可阅读、可定位回视频。
- ✅ **零登录**：公开视频无需账号 / Cookie 即可工作（受限视频可额外传入 Cookie）。
- ✅ **纯本地 / 开源 / 免费**：不依赖任何付费 API。

---

## 是否需要付费？（重点）

**不需要。** 本工具用到的全部是免费、公开的资源，没有账号订阅、没有按量计费的 API、没有密钥：

| 环节 | 用的什么 | 是否付费 |
| --- | --- | --- |
| 获取视频/字幕/音轨 | B 站公开 Web API | 免费（公开视频无需登录） |
| 中文语音识别 | FunASR 模型（paraformer / fsmn-vad / ct-punc） | 免费，从 ModelScope 自动下载 |
| 音频转码 | ffmpeg（开源） | 免费 |
| 运行环境 | 你自己的电脑（CPU 即可） | 免费 |

**你只需要付出「资源」，不是「钱」：**

- 网络流量：首次运行会从 ModelScope 下载约 **1GB** 的模型文件；识别时要下载视频音轨（几十~几百 MB）。
- 磁盘空间：模型 + 临时音频 + 输出文稿。
- 算力/时间：CPU 即可跑（13 分钟音频约 1 分钟识别完，rtf≈0.07）；有 NVIDIA GPU 可加 `--device cuda:0` 显著加速。

**可选的付费项（都不是必须的）：**

- 想要更高识别率/更快速度，可替换成商用 ASR（阿里云、腾讯云、讯飞、OpenAI Whisper API 等），但本工具默认不接、也不要求。
- B 站大会员对「公开视频」的音频提取**没有帮助**，无需开通。

---

## 工作原理

```
用户传入链接
   │
   ▼
[1] 解析 b23.tv / BV / av → 拿到 BV 号
   │
   ▼
[2] 调 view / player 接口 → 视频信息 + 字幕列表
   │
   ├─ 有字幕 ──► 下载字幕 JSON ──► 解析文本+时间戳 ──────┐
   │                                                      │
   └─ 无字幕 ──► playurl 拿音轨 ──► ffmpeg 转 wav ──► FunASR 转写 ┘
                                                              │
                                                              ▼
                                                  生成 Markdown 文稿
```

---

## 环境要求

- Python **≥ 3.9**（推荐 3.10/3.11）
- **ffmpeg**：系统级二进制，需单独安装（见下）
- 可联网（首次要下载模型）
- 磁盘：建议预留 ≥ 3GB

---

## 本地搭建部署（一步步来）

### 1. 克隆项目

```bash
git clone https://github.com/<你的用户名>/bili-transcript.git
cd bili-transcript
```

> 还没建 GitHub 仓库？见文末「发布到 GitHub」一节。

### 2. 安装 ffmpeg（必须，且不能用 pip）

- **macOS**（Homebrew）：
  ```bash
  brew install ffmpeg
  ```
- **Ubuntu / Debian**：
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```
- **Windows**（推荐 Chocolatey，或去 https://ffmpeg.org 下载解压并把 bin 加入 PATH）：
  ```powershell
  choco install ffmpeg
  ```
- 验证：`ffmpeg -version` 有输出即成功。

### 3. 创建虚拟环境并安装 Python 依赖

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .                  # 等价于安装 requirements.txt 中的依赖，并注册 bili-transcript 命令
```

> 不想用虚拟环境也可直接 `pip install -r requirements.txt`。
> 国内网络若下载慢，可加 `-i https://pypi.tuna.tsinghua.edu.cn/simple`。

### 4. 运行

```bash
# 最简：自动判断字幕 / ASR
bili-transcript "https://b23.tv/xxxxxx"

# 或者直接调用模块
python -m bili_transcript "https://www.bilibili.com/video/BV1xx411c7mD"
```

首次运行会在 `~/.cache/modelscope`（或 FunASR 缓存目录）下载约 1GB 模型，**请耐心等待**，之后复用。

---

## 使用说明

```bash
# 指定输出文件名
bili-transcript "视频链接" -o 讲稿.md

# 只看字幕，不要就退出（不下载音频做识别）
bili-transcript "视频链接" --no-asr

# 有 NVIDIA 显卡，用 GPU 加速
bili-transcript "视频链接" --device cuda:0

# 应用自定义校对词典（参见 examples/corrections_demo.json）
bili-transcript "视频链接" --corrections examples/corrections_demo.json

# 保留下载的音频（默认识别完会删除临时文件）
bili-transcript "视频链接" --keep-audio --workdir ./tmp
```

| 参数 | 说明 |
| --- | --- |
| `url` | 必填，b23.tv 短链 / BV 号页面 / av 号页面 |
| `-o, --output` | 输出 Markdown 路径，默认 `<视频标题>.md` |
| `--device` | ASR 设备，`cpu`（默认）或 `cuda:0` |
| `--no-asr` | 仅尝试字幕；无字幕直接退出，不识别 |
| `--corrections` | 可选的校对 JSON 词典路径 |
| `--keep-audio` | 保留下载的音频临时文件 |
| `--workdir` | 临时文件目录（默认当前目录） |

### 受限视频（地区/登录限制）

若提示无法获取音频地址，可把浏览器里登录后的 Cookie 通过环境变量传入：

```bash
export BILI_COOKIE="SESSDATA=xxxx; buvid3=xxxx; ..."   # bash
# 仅本次生效，不要提交到仓库
bili-transcript "视频链接"
```

---

## 输出格式

生成的 Markdown 包含：

1. **元信息**：来源链接、UP主、时长、BV 号、生成说明。
2. **段落版**：按句聚合的连续文本，便于通读。
3. **时间戳版**：每句带 `[mm:ss]`，方便定位回视频原声。

字幕路径与 ASR 路径输出格式完全一致，只是 `[来源]` 标注不同（字幕-中文 / 语音识别(ASR)）。

---

## 项目结构

```
bili-transcript/
├── README.md
├── requirements.txt
├── pyproject.toml
├── LICENSE
├── .gitignore
├── bili_transcript/          # 核心包
│   ├── __init__.py
│   ├── config.py             # 常量与模型配置
│   ├── api.py                # B站 API：解析/信息/字幕列表/音轨
│   ├── subtitles.py          # 字幕抓取与解析
│   ├── download.py           # 音频下载 + ffmpeg 转码
│   ├── asr.py                # FunASR 中文识别
│   ├── utils.py              # 时间戳/分段/校对/Markdown 生成
│   ├── cli.py                # 命令行入口
│   └── __main__.py           # 支持 python -m 运行
├── examples/
│   ├── corrections_demo.json # 校对词典示例（某视频专用，勿当通用规则）
│   └── sample_output.md      # 输出格式示例
└── tests/
    └── test_utils.py         # 纯函数单测
```

---

## 测试

```bash
pip install -e ".[dev]"
pytest tests/
```

---

## 局限性与 FAQ

- **Q：为什么有的视频抓不到字幕也识别不了？**
  A：可能是地区限制、需登录（大会员/付费视频）、或音频接口被限流。尝试设置 `BILI_COOKIE`。
- **Q：ASR 识别有错别字？**
  A：口语化、专有名词、英文/方言容易误识。可用 `--corrections` 传入自己的校对词典修正（注意：校对词典应针对具体视频，不要跨视频通用）。
- **Q：能批量处理多个视频吗？**
  A：当前是单链接 CLI。可写个 shell/Python 循环调用，例如 `for u in $(cat urls.txt); do bili-transcript "$u"; done`。
- **Q：能导出 .docx / .srt 吗？**
  A：目前输出 Markdown。时间戳版已是标准 `[mm:ss] 文本` 结构，转 SRT/Word 很容易在此基础上扩展（欢迎 PR）。

---

## 发布到 GitHub（把项目推上去）

如果你是在本地从零开始、还没建仓库：

```bash
cd bili-transcript
git init
git add .
git commit -m "feat: 初版 B站字幕/讲稿提取工具"

# 方式一：用 GitHub CLI（需先 gh auth login）
gh repo create bili-transcript --public --source=. --push

# 方式二：先在 github.com 新建空仓库，再关联推送
git remote add origin https://github.com/<你的用户名>/bili-transcript.git
git branch -M main
git push -u origin main
```

> 注意：`.gitignore` 已忽略 `.venv/`、`*.wav`、`*.m4s` 等，不会把模型和临时音频提交上去。

---

## 许可证

[MIT](LICENSE)
