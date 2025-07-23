import os
import threading
import time
import chardet

# 🔍 Ключові слова для пошуку
KEYWORDS = ["error", "warning", "critical"]

# 📁 Директорія з файлами для обробки
TARGET_DIR = r"C:\projects\ДЗ4_Половінкін Олексій"

# 📦 Синхронізація для результатів
lock = threading.Lock()

def process_files_thread(file_list, keywords, results):
    """Обробляє список файлів у потоці, шукаючи ключові слова.

    Args:
        file_list: Список імен файлів для обробки.
        keywords: Список ключових слів для пошуку.
        results: Словник для зберігання результатів (ключ: слово, значення: список шляхів).
    """
    local_results = {key: [] for key in keywords}

    for filename in file_list:
        file_path = os.path.join(TARGET_DIR, filename)
        try:
            # Спроба визначити кодування файлу
            with open(file_path, "rb") as f:
                raw_data = f.read()
                detected = chardet.detect(raw_data)
                encoding = detected["encoding"] if detected["encoding"] else "utf-8"

            # Читання файлу з визначеним або запасним кодуванням
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    for line in f:
                        line = line.lower()
                        for key in keywords:
                            if key.lower() in line:
                                if file_path not in local_results[key]:
                                    local_results[key].append(file_path)
                                break  # Уникаємо повторного додавання
            except UnicodeDecodeError:
                # Спроба з запасним кодуванням
                with open(file_path, "r", encoding="cp1251") as f:
                    for line in f:
                        line = line.lower()
                        for key in keywords:
                            if key.lower() in line:
                                if file_path not in local_results[key]:
                                    local_results[key].append(file_path)
                                break
        except Exception as e:
            print(f"Помилка при читанні файлу {file_path}: {e}")

    # 🔒 Додаємо результати до загального словника
    with lock:
        for key in keywords:
            results[key].extend(local_results[key])

def main():
    """Основна функція для багатопотокової обробки файлів."""
    start_time = time.time()

    # 📄 Отримуємо список .txt файлів
    all_files = [f for f in os.listdir(TARGET_DIR) if f.endswith(".txt")]

    # Перевірка на наявність файлів
    if not all_files:
        print("У директорії немає .txt файлів для обробки.")
        return

    # 🧵 Кількість потоків
    num_threads = 4
    chunk_size = len(all_files) // num_threads + 1
    threads = []
    results = {key: [] for key in KEYWORDS}

    for i in range(num_threads):
        file_chunk = all_files[i*chunk_size : (i+1)*chunk_size]
        t = threading.Thread(target=process_files_thread, args=(file_chunk, KEYWORDS, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()

    # 🧾 Виводимо результати
    print("Результати пошуку (threading):")
    for key, files in results.items():
        print(f"{key}: {files}")

    print(f"\nЧас виконання (threading): {end_time - start_time:.2f} секунд")

if __name__ == "__main__":
    main()