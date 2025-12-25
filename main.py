import asyncio
import os
import time
import pygame
import speech_recognition as sr
import edge_tts
from openai import OpenAI
import pvporcupine
from pvrecorder import PvRecorder
from faster_whisper import WhisperModel

# ================= 🔧 配置区域 (必改) =================

# 1. 你的 DeepSeek API Key
DEEPSEEK_API_KEY = "sk-36310dd6b0ba469ea7e82a3e5b57a766"

# 2. 你的 Picovoice AccessKey (控制台首页那个)
PICOVOICE_ACCESS_KEY = "I5CWkBsx37yttJBbKPSUtpJcZI1kZXiERkf6YgJuI3SBaCkMgjQvVA=="

# 3. 你的唤醒词文件路径 (刚才下载并改名的文件)
# 如果文件和代码在同一个文件夹，直接填文件名
WAKE_WORD_PATH = "gouzi.ppn"

# =======================================================

# --- 全局初始化 ---

print("[*] 正在加载 Faster-Whisper 模型 (首次运行会自动下载)...")
# 使用 int8 量化加速，CPU 也能飞快运行
try:
    stt_model = WhisperModel("small", device="cpu", compute_type="int8")
    print("[*] 模型加载完成！")
except Exception as e:
    print(f"[!] Whisper 模型加载失败，请检查网络或FFmpeg: {e}")
    exit()

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
pygame.mixer.init()


def play_audio(file_path):
    """播放音频"""
    if not os.path.exists(file_path):
        return
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"[!] 播放出错: {e}")


async def text_to_speech(text):
    """Edge-TTS 语音合成"""
    output_file = "reply.mp3"
    # 使用中文女声：zh-CN-XiaoxiaoNeural
    try:
        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await communicate.save(output_file)
        return output_file
    except Exception as e:
        print(f"[!] TTS生成失败: {e}")
        return None


def call_deepseek(query):
    """DeepSeek 思考"""
    print(f"[*] DeepSeek 思考中: {query}")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个中文语音助手。请用简短、口语化的中文回答(50字以内)。",
                },
                {"role": "user", "content": query},
            ],
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[!] API请求失败: {e}")
        return "我好像断网了。"


def listen_and_transcribe():
    """录音并识别"""
    r = sr.Recognizer()
    mic = sr.Microphone()
    temp_wav = "temp.wav"

    with mic as source:
        print(">> 请说话 (Listening)...")
        r.adjust_for_ambient_noise(source, duration=0.5)

        try:
            # 录音：5秒无声超时，最长录10秒
            audio = r.listen(source, timeout=5, phrase_time_limit=10)

            with open(temp_wav, "wb") as f:
                f.write(audio.get_wav_data())

            print(">> 正在识别...")
            # 使用 Faster-Whisper 识别中文
            segments, _ = stt_model.transcribe(temp_wav, language="zh", beam_size=5)
            text = "".join([s.text for s in segments]).strip()

            print(f">> 收到: {text}")
            return text if text else None

        except sr.WaitTimeoutError:
            print("[!] 未检测到语音")
            return None
        except Exception:
            return None
        finally:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)


async def main():
    # 1. 加载唤醒词
    if not os.path.exists(WAKE_WORD_PATH):
        print(f"[错误] 找不到唤醒词文件: {WAKE_WORD_PATH}")
        return

    try:
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY, keyword_paths=[WAKE_WORD_PATH]
        )
    except Exception as e:
        print(f"[!] 唤醒引擎初始化失败: {e}")
        return

    recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

    print(f"\n{'='*40}")
    print(f" 系统就绪 | 请说唤醒词")
    print(f"{'='*40}\n")

    try:
        recorder.start()
        while True:
            pcm = recorder.read()
            # 检测唤醒
            if porcupine.process(pcm) >= 0:
                print(f"\n[O] 唤醒成功！")
                recorder.stop()

                # 开始交互
                user_text = listen_and_transcribe()
                if user_text:
                    reply = call_deepseek(user_text)
                    print(f"[A] AI: {reply}")

                    audio = await text_to_speech(reply)
                    if audio:
                        play_audio(audio)
                        os.remove(audio)

                print("[*] 等待唤醒...")
                recorder.start()

    except KeyboardInterrupt:
        print("退出。")
    finally:
        recorder.delete()
        porcupine.delete()


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
