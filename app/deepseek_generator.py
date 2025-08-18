from openai import OpenAI
from settings import DEEP_SEEK_API_KEY, DEEP_SEEK_BASE_URL, TEMPERATURE

def generate_text(prompt: str, text: str) -> str:
    """Генерирует Telegram-пост на основе промта и распознанного текста.
    
    Args:
        prompt: Шаблон промта для генерации
        text: Распознанный текст для обработки
        
    Returns:
        Сгенерированный текст поста
    """
    client = OpenAI(
        api_key=DEEP_SEEK_API_KEY,
        base_url=DEEP_SEEK_BASE_URL
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user", 
                "content": f"{prompt}\n\n{text}"
            }],
            temperature=TEMPERATURE
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Ошибка при генерации текста: {e}")
        return "Error when generating text. Check the logs."
