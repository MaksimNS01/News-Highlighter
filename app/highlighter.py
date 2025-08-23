from moviepy import VideoFileClip
from pydub import AudioSegment
import numpy as np
import os

from functions import delete_file

def extract_audio(video_path, audio_path):
    """Извлекает аудиодорожку из видео."""
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path, fps=16000, nbytes=2, codec='pcm_s16le')
    audio.close()
    video.close()

    return audio_path

def get_loud_segments(audio_path, threshold=0.03, min_silence_duration=2.0, min_segment_duration=15.0):
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

    # Удаляем временный файл
    delete_file(audio_path)

    return segments

def create_highlights(video_path, segments, output_dir):
    # Получаем имя файла без расширения
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # Создаем папку с именем видео внутри output_dir
    video_output_dir = os.path.join(output_dir, video_name)
    os.makedirs(video_output_dir, exist_ok=True)

    video = VideoFileClip(video_path)
    
    video_names = []

    for i, (start, end) in enumerate(segments):
        clip = video.subclipped(start, end)  # Исправлено: subclip вместо subclipped
        # Формируем имя в стиле "hl{i}_{video_name}"
        output_filename = f"hl{i}_{video_name}.mp4"
        video_names.append(output_filename)
        output_path = os.path.join(video_output_dir, output_filename)
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        print(f"Хайлайт сохранен: {output_path}")

    video.close()

    return video_output_dir, video_names
