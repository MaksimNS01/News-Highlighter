from moviepy import VideoFileClip#, concatenate_videoclips
from pydub import AudioSegment
import numpy as np
import os

def extract_audio(video_path, audio_path):
    """Извлекает аудиодорожку из видео."""
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path, fps=16000, nbytes=2, codec='pcm_s16le')
    audio.close()
    video.close()

def get_loud_segments(audio_path, threshold=0.02, min_silence_duration=1.0, min_segment_duration=5.0):
    """Анализирует аудио и возвращает временные метки громких сегментов."""
    audio = AudioSegment.from_wav(audio_path)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples = samples / np.max(np.abs(samples))  # Нормализация

    chunk_size = int(0.1 * 1000)  # 100 мс
    loud_chunks = []

    for i in range(0, len(audio), chunk_size):
        chunk = samples[int(i * len(samples) / len(audio)):int((i + chunk_size) * len(samples) / len(audio))]
        if np.mean(np.abs(chunk)) > threshold:
            loud_chunks.append(i / 1000.0)  # в секундах

    # Группируем сегменты
    segments = []
    if not loud_chunks:
        return segments

    start = loud_chunks[0]
    for i in range(1, len(loud_chunks)):
        if loud_chunks[i] - loud_chunks[i - 1] > min_silence_duration:
            duration = loud_chunks[i - 1] - start
            if duration >= min_segment_duration:
                segments.append((start, loud_chunks[i - 1]))
            start = loud_chunks[i]
    # Последний сегмент
    duration = loud_chunks[-1] - start
    if duration >= min_segment_duration:
        segments.append((start, loud_chunks[-1]))

    return segments

def create_highlights(video_path, segments, output_dir="highlights"):
    """Соаздет хайлайты."""

    #             ,           
    os.makedirs(output_dir, exist_ok=True)

    video = VideoFileClip(video_path)

    for i, (start, end) in enumerate(segments):
        clip = video.subclipped(start, end)
        output_path = os.path.join(output_dir, f"highlight_{i+1:03d}.mp4")
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        print(f"               : {output_path}")

    video.close()
