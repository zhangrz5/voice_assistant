# 🤖 中文语音助手 (Chinese Voice Assistant)

这是一个基于 **DeepSeek**、**Faster-Whisper**、**Edge-TTS** 和 **Picovoice** 构建的高性能中文语音助手。它具备离线唤醒、快速语音识别、智能对话和自然语音合成功能。


**输出规范**
> **语言要求**：所有回复、思考过程及任务清单，均须使用中文。
> **固定指令**：`Implementation Plan, Task List and Thought in Chinese`

## ✨ 功能特性

*   **👂 离线唤醒**: 使用 Picovoice Porcupine 实现低功耗、高精度的离线唤醒词检测。
*   **🎙️ 语音识别**: 集成 Faster-Whisper 模型，支持 CPU 推理，识别速度快，中文准确率高。
*   **🧠 智能大脑**: 接入 DeepSeek V3 大模型，提供流畅、自然的对话体验。
*   **🗣️ 语音合成**: 使用 Edge-TTS 生成高质量的中文语音回复。

## 🛠️ 环境要求

*   **系统**: Windows (项目代码针对 Windows 的 `asyncio` 策略进行了适配，Linux/Mac 可能需要微调 `main.py` 最后的事件循环设置)。
*   **Python**: 3.8 或更高版本。
*   **FFmpeg**: 必须安装并配置到系统环境变量中 (用于音频处理)。

## 📦 安装指南

1.  **克隆或下载本项目**

2.  **安装依赖库**
    打开终端，运行以下命令安装所需的 Python 库：

    ```bas
    conda create -n voice_assistant python=3.10 -y

    conda activate voice_assistant

    conda install ffmpeg -y

    # 安装核心库：加速版语音识别、DeepSeek调用、语音合成、离线唤醒、音频播放
    pip install faster-whisper openai edge-tts pvporcupine pvrecorder pygame SpeechRecognition
    ```

## ⚙️ 配置说明

在运行之前，你需要修改 `main.py` 文件中的配置区域：

1.  **DeepSeek API Key**
    *   注册并获取 [DeepSeek API Key](https://www.deepseek.com/)。
    *   修改 `main.py` 第 15 行：
        ```python
        DEEPSEEK_API_KEY = "sk-你的API密钥"
        ```

2.  **Picovoice AccessKey**
    *   注册 [Picovoice Console](https://console.picovoice.ai/) 账号。
    *   复制首页的 `AccessKey`。
    *   修改 `main.py` 第 18 行：
        ```python
        PICOVOICE_ACCESS_KEY = "你的AccessKey"
        ```

3.  **唤醒词文件**
    *   在 Picovoice Console 下载适用于 Windows 的唤醒词文件 (`.ppn`)。
    *   将文件放入项目目录。
    *   修改 `main.py` 第 22 行：
        ```python
        WAKE_WORD_PATH = "你的唤醒词文件名.ppn" 
        # 例如: "xiaodi.ppn"
        ```

## 🚀 运行方法

在终端中运行：

```bash
python main.py
```

**首次运行注意**:
*   程序会自动下载 Faster-Whisper 模型 (约 500MB+)，请保持网络通畅。
*   看到 `System Ready | 请说唤醒词` 提示后，即可对着麦克风说出唤醒词。

## 📝 注意事项

*   **Privacy**: 请妥善保管你的 API Key 和 AccessKey，不要上传到公共代码仓库。
*   **Network**: 语音合成和 DeepSeek API 调用需要联网。
*   **Audio**: 确保电脑麦克风和扬声器工作正常。

## 📄 License

MIT License
