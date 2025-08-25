import yt_dlp
import os

def download_instagram_video(video_url, output_path='.'):
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'), # Название файла и расширение
        'format': 'bestvideo+bestaudio/best', # Выбирает лучшее качество
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    print(f"Видео с '{video_url}' успешно загружено!")

if __name__ == "__main__":
    video_url = input("Введите ссылку на видео из Instagram: ")
    download_instagram_video(video_url)