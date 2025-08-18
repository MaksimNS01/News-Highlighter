from highlighter import extract_audio, get_loud_segments, create_highlights
from vosk_recognizer import recognize_audio
from deepseek_generator import generate_text
from functions import split_post, add_previews_to_videos, save_json
from settings import PROMPT, ADDING_INTRO

# Основной скрипт
if __name__ == "__main__":
    # 0. Пути сохранения
    input_video = "./media/test_videos/long1.mp4"
    audio_temp = "./temp/temp_audio.wav"
    output_video = "./media/result_videos"

    # 1. Создание хайлайтов
    print("\nИзвлечение аудио...")
    extract_audio(input_video, audio_temp)

    print("\nАнализ аудио...")
    segments = get_loud_segments(audio_temp, threshold=0.02, min_segment_duration=4.0)

    print(f"Найдено {len(segments)} сегментов.")
    for s in segments:
        print(f"Продолжительность {s[1]:.2f} секунд")
        # print(f"Продолжительность {s[0]:.2f} - {s[1]:.2f} секунд")

    print("\nСоздание хайлайтов...")
    video_output_dir, video_name = create_highlights(input_video, segments, output_video)

    print(f"\nВидео сохранено: {video_output_dir}")

    # 2. Вставка интро в хайлайты
    if ADDING_INTRO:
        print("\nДобавление интро...")
        add_previews_to_videos(
            result_videos_folder = video_output_dir,
            previews_folder = "./media/intro",
        )

    # 3. Распознавание текста
    test_audio = './temp/temp_audio.wav'
    print()
    test_text = recognize_audio(test_audio)
    print(f"Текст успешно распознан: {test_text[:50]}...")

    # 4. Создание поста для телеграм
    print("\nГенерация поста с помощью Deep Seek...")
    test_generated_post = generate_text(PROMPT, test_text)
    # print(test_generated_post)
    header, content = split_post(test_generated_post)
    print(f"Пост успешно сгенерирован с заголовком: {header}")

    # 5. Сохранение метаданных в .json-файл
    print("\nСохранение метаданных в .json-файл...")
    json_data = save_json(header, segments, test_generated_post, video_output_dir, video_name)
