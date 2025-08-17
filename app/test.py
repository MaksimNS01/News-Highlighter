from highlighter import extract_audio, get_loud_segments, create_highlights
from vosk_recognizer import recognize_audio

# Основной скрипт
if __name__ == "__main__":
    input_video = "./media/test_videos/short1.mp4"
    audio_temp = "temp/temp_audio.wav"
    output_video = "./media/result_videos"

    print("\nИзвлечение аудио...")
    extract_audio(input_video, audio_temp)

    print("\nАнализ аудио...")
    segments = get_loud_segments(audio_temp, threshold=0.02, min_segment_duration=4.0)

    print(f"Найдено {len(segments)} сегментов.")
    for s in segments:
        print(f"  {s[0]:.2f} - {s[1]:.2f} секунд")

    print("\nСоздание хайлайтов...")
    create_highlights(input_video, segments, output_video)

    print(f"\nВидео сохранено: {output_video}")

    test_audio = './temp/temp_audio.wav'
    print()
    test_text = recognize_audio(test_audio)
    print(f"Полный распознанный текст: {test_text}")
