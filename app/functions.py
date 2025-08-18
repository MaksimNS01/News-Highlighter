import re
import os
import json
from moviepy import VideoFileClip, concatenate_videoclips

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
                os.remove(video_path)

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
