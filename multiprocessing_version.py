import os
import time
from multiprocessing import Process, Queue, current_process
import chardet
from queue import Empty  # Додано імпорт для обробки винятку

# 🔍 Ключові слова для пошуку
KEYWORDS = ["error", "warning", "critical"]

# 📁 Директорія з файлами для обробки
TARGET_DIR = r"C:\projects\ДЗ4_Половінкін Олексій"

def process_files_proc(file_list, keywords, queue):
    """Обробляє список файлів у процесі, шукаючи ключові слова.

    Args:
        file_list: Список імен файлів для обробки.
        keywords: Список ключових слів для пошуку.
        queue: Черга для передачі результатів у головний процес.
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
            print(f"Помилка при читанні файлу {file_path} у процесі {current_process().name}: {e}")

    # Надсилаємо результати через чергу
    queue.put(local_results)

def main():
    """Основна функція для багатопроцесорної обробки файлів."""
    start_time = time.time()

    # 📄 Отримуємо список .txt файлів
    all_files = [f for f in os.listdir(TARGET_DIR) if f.endswith(".txt")]

    # Перевірка на наявність файлів
    if not all_files:
        print("У директорії немає .txt файлів для обробки.")
        return

    # 🛠 Кількість процесів
    num_processes = 4
    chunk_size = len(all_files) // num_processes + 1
    queue = Queue()
    processes = []

    for i in range(num_processes):
        file_chunk = all_files[i*chunk_size : (i+1)*chunk_size]
        p = Process(target=process_files_proc, args=(file_chunk, KEYWORDS, queue))
        processes.append(p)
        p.start()

    # Збираємо результати з усіх процесів
    results = {key: [] for key in KEYWORDS}
    for _ in processes:
        try:
            proc_result = queue.get(timeout=10)  # Тайм-аут 10 секунд
            for key in KEYWORDS:
                results[key].extend(proc_result.get(key, []))
        except Empty:
            print("Помилка: тайм-аут при отриманні результатів із черги.")

    for p in processes:
        p.join()

    end_time = time.time()

    # 🧾 Виводимо результати
    print("Результати пошуку (multiprocessing):")
    for key, files in results.items():
        print(f"{key}: {files}")

    print(f"\nЧас виконання (multiprocessing): {end_time - start_time:.2f} секунд")

if __name__ == "__main__":
    main()