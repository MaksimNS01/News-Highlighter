import os
import vosk
from pathlib import Path

from highlighter import extract_audio, get_loud_segments, create_highlights
from vosk_recognizer import recognize_audio
from deepseek_generator import generate_text
from functions import split_post, add_previews_to_videos, save_json, delete_file, add_title_frame_to_video, smart_split
from settings import PROMPT, ADDING_INTRO, FONT_TYPE, LEFT_MARGIN, LINE_HEIGHT, FONT_SIZE, BLUE_Y, RED_Y

# Основной скрипт
if __name__ == "__main__":
    # 0. Пути сохранения
    input_video = "./media/test_videos/short1.mp4"
    audio_temp = "./temp/temp_audio.wav"
    output_video = "./media/result_videos"

    # Путь до модели
    model_path = "./models/vosk-model-ru-0.42"

    # Проверяем существование модели
    if not os.path.exists(model_path):
        print(f"Модель не найдена по пути: {model_path}")
        exit(1)

    # Отключаем логи Vosk
    vosk.SetLogLevel(-1)

    # Инициализация модели
    print("Инициализация модели Vosk...")
    model = vosk.Model(model_path)

    # 1. Создание хайлайтов
    print("\nИзвлечение аудио...")
    extracted_audio = extract_audio(input_video, audio_temp)

    print("\nАнализ аудио...")
    segments = get_loud_segments(audio_temp, threshold=0.02, min_segment_duration=4.0)

    print(f"Найдено {len(segments)} сегментов.")
    for s in segments:
        print(f"Продолжительность {s[1]:.2f} секунд")
        # print(f"Продолжительность {s[0]:.2f} - {s[1]:.2f} секунд")

    print("\nСоздание хайлайтов...")
    video_output_dir, video_names = create_highlights(input_video, segments, output_video)

    print(f"\nВидео сохранено: {video_output_dir}")

    # 2. Вставка интро в хайлайты
    if ADDING_INTRO:
        print("\nДобавление интро...")
        add_previews_to_videos(
            result_videos_folder = video_output_dir,
            previews_folder = "./media/intro",
        )
    
    # Обработка всех видеофайлов в папке
    video_files = [f for f in os.listdir(video_output_dir) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    if not video_files:
        print(f"В папке {video_output_dir} не найдено видеофайлов")
    else:
        print(f"Найдено {len(video_files)} видеофайлов для обработки")

    for video_file in video_files:
        try:
            # Формируем полные пути
            video_path = os.path.join(video_output_dir, video_file)
            video_name = Path(video_file).stem  # Имя файла без расширения
            
            print(f"\n{'='*50}")
            print(f"Обработка видео: {video_file}")
            print(f"{'='*50}")
            
            audio_temp = f"./temp/temp_audio_{video_name}.wav"
            print("\nИзвлечение аудиодорожки...")
            extracted_audio = extract_audio(video_path, audio_temp)
            
            # 3. Распознавание текста
            recognized_text = recognize_audio(extracted_audio, model)
            print(f"Текст успешно распознан: {recognized_text[:50]}...")
            
            # 4. Создание поста для телеграм
            print("\nГенерация поста с помощью Deep Seek...")
            generated_post = generate_text(PROMPT, recognized_text)
            header, content = split_post(generated_post)
            
            # 5. Сохранение метаданных в .json-файл
            print("\nСохранение метаданных...")
            json_data = save_json(
                header=header,
                segments=segments,
                generated_post=generated_post,
                path_to_save=video_output_dir,
                video_name=video_name
            )
            
            # 6. Добавление превью
            print("\nДобавление превью...")
            # Разделение заголовка на две части по смыслу
            first_line, second_line = smart_split(header)

            add_title_frame_to_video(
                video_path=video_path, 
                minutes=0, # минута таймкода
                seconds=15, # секунда таймкода
                line1=first_line, 
                line2=second_line,
                font_type=FONT_TYPE,
                left_margin=LEFT_MARGIN,
                line_height=LINE_HEIGHT,
                font_size=FONT_SIZE,
                blue_y=BLUE_Y,
                red_y=RED_Y
            )
            
            # Удаляем временный аудиофайл
            delete_file(audio_temp)
                
        except Exception as e:
            print(f"\nОшибка при обработке файла {video_file}: {str(e)}")
            continue
