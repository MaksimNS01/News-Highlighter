import re
import os
import json
import numpy as np
from moviepy import VideoFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

def split_post(post: str) -> tuple[str, str]:
    """
    Разделяет пост на заголовок и контент, удаляя Markdown-разметку и эмодзи.
    
    Args:
        post: Исходный текст поста (может содержать Markdown/HTML/эмодзи)
        
    Returns:
        Кортеж (заголовок_без_эмодзи, контент) без разметки
        
    Raises:
        ValueError: Если входные данные некорректны
    """
    try:
        if not isinstance(post, str):
            raise ValueError("Input must be a string")
            
        if not post.strip():
            return "", ""
        
        # Функция для очистки текста от разметки
        def clean_text(text: str) -> str:
            # Удаление Markdown
            text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)  # * **
            text = re.sub(r'_{1,2}(.*?)_{1,2}', r'\1', text)    # _ __
            text = re.sub(r'`{1,3}(.*?)`{1,3}', r'\1', text)    # ` ```
            text = re.sub(r'~~(.*?)~~', r'\1', text)            # ~~
            text = re.sub(r'<[^>]+>', '', text)                 # HTML-теги
            text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)     # [ссылки](url)
            return text.strip()
        
        # Функция для удаления эмодзи
        def remove_emojis(text: str) -> str:
            # Диапазоны Unicode для эмодзи
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # эмоции
                "\U0001F300-\U0001F5FF"  # символы
                "\U0001F680-\U0001F6FF"  # транспорт
                "\U0001F700-\U0001F77F"  # алхимия
                "\U0001F780-\U0001F7FF"  # геометрические фигуры
                "\U0001F800-\U0001F8FF"  # дополнение
                "\U0001F900-\U0001F9FF"  # дополнение 2
                "\U0001FA00-\U0001FA6F"  # шахматы
                "\U0001FA70-\U0001FAFF"  # символы
                "\U00002702-\U000027B0"  # доп. символы
                "\U000024C2-\U0001F251" 
                "]+",
                flags=re.UNICODE
            )
            return emoji_pattern.sub('', text).strip()
        
        # Разделяем пост на строки
        lines = post.split('\n', 1)
        
        # Очищаем заголовок от разметки И эмодзи
        header = remove_emojis(clean_text(lines[0]))
        
        # Очищаем контент только от разметки (эмодзи остаются)
        content = clean_text(lines[1]) if len(lines) > 1 else ""
        
        return header, content
        
    except Exception as e:
        # Логирование ошибки при необходимости
        print(f"Error processing post: {str(e)}")
        return "", ""

def add_previews_to_videos(result_videos_folder, previews_folder):
    # Пути к превью
    square_preview_path = os.path.join(previews_folder, "square_preview.mp4")
    rectangular_preview_path = os.path.join(previews_folder, "rectangular_preview.mp4")

    if not os.path.exists(square_preview_path):
        raise FileNotFoundError(f"Файл не найден: {square_preview_path}")
    if not os.path.exists(rectangular_preview_path):
        raise FileNotFoundError(f"Файл не найден: {rectangular_preview_path}")

    for filename in os.listdir(result_videos_folder):
        if filename.endswith((".mp4", ".avi", ".mov", ".mkv")):
            video_path = os.path.join(result_videos_folder, filename)
            video_name = os.path.splitext(filename)[0]  # Имя без расширения
            video_extension = os.path.splitext(filename)[1]  # Расширение файла
            
            # Новое имя файла с добавлением буквы "i"
            new_filename = f"i_{video_name}{video_extension}"
            new_video_path = os.path.join(result_videos_folder, new_filename)

            try:
                # Загружаем основное видео
                video_clip = VideoFileClip(video_path)
                width, height = video_clip.size
                aspect_ratio = width / height

                # Выбираем превью по соотношению сторон
                if abs(aspect_ratio - 1.0) < 0.1:  # 1:1
                    preview_path = square_preview_path
                elif abs(aspect_ratio - 16/9) < 0.1:  # 16:9
                    preview_path = rectangular_preview_path
                else:
                    print(f"Пропущено: неизвестное соотношение сторон {aspect_ratio} для {filename}")
                    video_clip.close()
                    continue

                # Загружаем превью
                preview_clip = VideoFileClip(preview_path)

                # Устанавливаем размер превью равным размеру основного видео
                preview_resized = preview_clip.resized((width, height))

                # Конкатенируем: превью + видео
                final_clip = concatenate_videoclips([preview_resized, video_clip])

                # Сохраняем по новому пути
                final_clip.write_videofile(
                    new_video_path,
                    codec="libx264",
                    audio_codec="aac",
                    preset="medium",
                    bitrate="5000k",
                    ffmpeg_params=["-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2"]
                )

                # Освобождаем ресурсы
                preview_clip.close()
                video_clip.close()
                final_clip.close()

                # Удаляем исходное видео
                delete_file(video_path)

                print(f"Обработано: {filename} → {new_filename}")

            except Exception as e:
                print(f"Ошибка при обработке {filename}: {e}")

def save_json(
        header="", 
        segments=[], 
        generated_post="", 
        path_to_save=".", 
        video_name=""
        ):
    # Формируем имя файла
    filename = f"{video_name}_metadata.json"
    
    # Убедимся, что path_to_save — это путь к файлу, а не папке
    if os.path.isdir(path_to_save):
        path_to_save = os.path.join(path_to_save, filename)  # добавляем имя файла

    # Создаём папку, если её нет
    os.makedirs(os.path.dirname(path_to_save) if os.path.dirname(path_to_save) else ".", exist_ok=True)

    # Подготавливаем данные
    output_data = {
        "Header": header,
        "Number of segments": len(segments),
        "Duration, sec": segments,
        "Generated post": generated_post
    }

    # Записываем в файл
    with open(path_to_save, 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=2)

    print(f"Результат сохранен в {path_to_save}")
    return output_data

def add_title_frame_to_video(video_path, minutes, seconds, line1, line2, font_type="arial.ttf", left_margin=0, line_height=80, font_size=64, blue_y=0.6, red_y=0.7):
    try:
        # Проверка существования файла
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Видео не найдено: {video_path}")

        # Загрузка видео
        video = VideoFileClip(video_path)
        total_duration = video.duration  # в секундах

        # Проверка корректности таймкода
        target_time = minutes * 60 + seconds
        if target_time >= total_duration or target_time < 0:
            raise ValueError("Указанный таймкод выходит за пределы длительности видео.")

        # Извлечение кадра
        frame = video.get_frame(t=target_time)  # numpy массив
        frame_img = Image.fromarray(frame)
        width, height = frame_img.size  # размеры кадра

        # Создание заголовка — рисуем прямо на кадре
        combined = frame_img.copy()
        draw = ImageDraw.Draw(combined)

        try:
            # Попробуем загрузить шрифт
            font = ImageFont.truetype(font_type, font_size)
        except Exception as e:
            # Если не удалось, используем стандартный
            print(f"Не удалось загрузить шрифт {font_type}, используем стандартный. Ошибка: {e}")
            font = ImageFont.load_default()

        # Размеры текста
        bbox1 = draw.textbbox((0, 0), line1, font=font)
        bbox2 = draw.textbbox((0, 0), line2, font=font)
        text_width1 = bbox1[2] - bbox1[0]
        text_width2 = bbox2[2] - bbox2[0]

        # Синий прямоугольник (60% от верха)
        y1 = int(blue_y * height)
        draw.rectangle(
            [left_margin, y1, left_margin + text_width1 + 30, y1 + line_height],
            fill=(0, 0, 255)
        )
        draw.text((left_margin + 15, y1 + 5), line1, font=font, fill=(255, 255, 255))

        # Красный прямоугольник (65% от верха)
        y2 = int(red_y * height)
        draw.rectangle(
            [left_margin, y2, left_margin + text_width2 + 30, y2 + line_height],
            fill=(255, 0, 0)
        )
        draw.text((left_margin + 15, y2 + 5), line2, font=font, fill=(255, 255, 255))

        # Конвертация в numpy массив
        combined_np = np.array(combined)

        # Создание клипа из кадра с заголовком (длительность 0.5 секунды)
        title_clip = ImageClip(combined_np)
        title_clip = title_clip.with_duration(0.5)

        # Склеивание: заголовок + оригинальное видео
        final_video = concatenate_videoclips([title_clip, video])

        # Сохранение
        base_dir = os.path.dirname(video_path)
        base_name = os.path.basename(video_path)
        name, ext = os.path.splitext(base_name)
        output_path = os.path.join(base_dir, f"t{name}{ext}")

        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

        delete_file(video_path)

        print(f"Видео сохранено: {output_path}")

    except Exception as e:
        print(f"Ошибка: {e}")

def smart_split(text):
    words = text.split()
    if len(words) <= 3:  # For very short headers
        return text, ""
    
    # Try to split at common prepositions
    for split_at in ['за', 'на', 'о', 'в', 'по', 'для']:
        if f' {split_at} ' in text:
            before, after = text.split(f' {split_at} ', 1)
            return f"{before}", f"{split_at} {after}"
    
    # Fallback to middle split at space
    mid = len(words) // 2
    for i in range(mid, len(words)):
        if words[i] in ['и', 'или', 'но']:  # Split at conjunctions
            return ' '.join(words[:i]), ' '.join(words[i:])
    return ' '.join(words[:mid]), ' '.join(words[mid:])

def delete_file(audio_temp):
    # Удаляем временный аудиофайл
    if os.path.exists(audio_temp):
        os.remove(audio_temp)
        print(f"Временный аудиофайл {audio_temp} удален")
    else:
        print(f"Аудиофайл {audio_temp} не найден, удаление не выполнено.")
