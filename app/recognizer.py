import vosk
import json
import os
import wave
import array

def recognize_audio(audio_file_path):
    # Создаем директорию temp, если она не существует
    os.makedirs('./temp', exist_ok=True)

    # Путь до модели
    model_path = "./models/vosk-model-ru-0.42"

    # Проверяем существование модели
    if not os.path.exists(model_path):
        print(f"Модель не найдена по пути: {model_path}")
        exit(1)

    # Инициализация модели
    model = vosk.Model(model_path)

    # Проверяем существование аудио файла
    if not os.path.exists(audio_file_path):
        print(f"Аудио файл не найден: {audio_file_path}")
        exit(1)

    # Открываем WAV файл
    wf = wave.open(audio_file_path, "rb")

    # Проверяем и конвертируем аудио при необходимости
    sample_rate = wf.getframerate()
    channels = wf.getnchannels()
    sample_width = wf.getsampwidth()

    print(f"Исходные параметры: {sample_rate} Гц, {channels} канал(ов), {sample_width * 8} бит")

    # Если аудио стерео, создаем новый файл в моно
    if channels == 2:
        print("Конвертируем стерео в моно...")
        
        # Читаем все фреймы
        frames = wf.readframes(-1)
        
        # Закрываем оригинальный файл
        wf.close()
        
        # Конвертируем стерео в моно (берем только левый канал)
        if sample_width == 2:  # 16 бит
            audio_array = array.array('h', frames)
        elif sample_width == 1:  # 8 бит
            audio_array = array.array('b', frames)
        elif sample_width == 4:  # 32 бит
            audio_array = array.array('i', frames)
        else:
            print(f"Неподдерживаемая глубина звука: {sample_width * 8} бит")
            exit(1)
        
        # Берем только левый канал (каждый второй сэмпл)
        mono_frames = audio_array[::2]
        
        # Создаем временный моно файл
        mono_file_path = './temp/temp_audio_mono.wav'
        mono_wf = wave.open(mono_file_path, 'wb')
        mono_wf.setnchannels(1)  # моно
        mono_wf.setsampwidth(sample_width)
        mono_wf.setframerate(sample_rate)
        mono_wf.writeframes(mono_frames.tobytes())
        mono_wf.close()
        
        # Открываем моно файл для распознавания
        wf = wave.open(mono_file_path, "rb")
        print("Конвертация завершена")

    # Создаем распознаватель с правильной частотой дискретизации
    final_sample_rate = wf.getframerate()
    rec = vosk.KaldiRecognizer(model, final_sample_rate)

    # Читаем аудио данные и распознаем
    results = []
    chunk_size = 4000

    print("Начинаем распознавание...")

    while True:
        data_chunk = wf.readframes(chunk_size)
        if len(data_chunk) == 0:
            break
        if rec.AcceptWaveform(data_chunk):
            result = json.loads(rec.Result())
            if result['text']:
                results.append(result['text'])

    # Получаем финальный результат
    final_result = json.loads(rec.FinalResult())
    if final_result['text']:
        results.append(final_result['text'])

    # Объединяем все результаты
    recognized_text = ' '.join(results).strip()

    # # Сохраняем распознанный текст в файл ./temp/rt.json
    # output_data = {
    #     "recognized_text": recognized_text
    # }

    # with open('./temp/rt.json', 'w', encoding='utf-8') as output_file:
    #     json.dump(output_data, output_file, ensure_ascii=False, indent=2)

    # print("Результат сохранен в ./temp/rt.json")

    # Закрываем файл
    wf.close()

    # Удаляем аудио файлы
    os.remove(audio_file_path)
    os.remove(mono_file_path)

    # Возвращаем распознанный текст
    return recognized_text

test_audio = './temp/temp_audio.wav'
test_text = recognize_audio(test_audio)
print(f"Полный распознанный текст: {test_text}")
