import re

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
