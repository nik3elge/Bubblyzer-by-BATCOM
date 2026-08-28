# 💬 Bubblyzer by BATCOM

[![Release](https://img.shields.io/github/v/release/BATCOM/Bubblyzer?style=flat-square&color=38bdf8)](https://github.com)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue?style=flat-square)](https://github.com)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-ONNX%20Runtime%20%2B%20DirectML-success?style=flat-square)](https://onnxruntime.ai/)
[![Integration](https://img.shields.io/badge/Affinity-Publisher%20%26%20Designer%20v2-orange?style=flat-square)](https://affinity.serif.com/)

**Bubblyzer by BATCOM** — это автономное приложение на базе нейросети **YOLOv8 ONNX** для автоматического распознавания речевых пузырей (бабблов) на страницах комиксов и манги с мгновенной расстановкой текстовых фреймов в **Affinity by Canva**.

---

## ✨ Возможности

- ⚡ **Высокая скорость (ONNX Runtime):** Дистрибутив весит в разы меньше классических PyTorch-решений и запускается за доли секунды.
- 🎮 **Аппаратное ускорение из коробки:**
  - **Windows:** `DirectML` (работает на **любых** видеокартах: NVIDIA, AMD Radeon, Intel Arc / UHD).
  - **macOS:** `CoreML` (полная поддержка Apple Silicon M1/M2/M3/M4 и Neural Engine).
  - **Автоматический откат на CPU:** если GPU недоступен, сервер бесшовно продолжит работу на процессоре.
- 💬 **Нативная интеграция с Affinity by Canva:** Скрипт `affinity_bubblyzer.js` экспортирует страницу, опрашивает локальный сервер и автоматически создает текстовые фреймы (`Frame Text`) точного размера прямо поверх найденных бабблов.
- 🎛️ **Удобство и тихий режим:** Приложение работает в фоновом режиме в системном трее Windows/macOS.
- 🔒 **100% Оффлайн и конфиденциально:** Все изображения обрабатываются локально на вашем компьютере, данные никуда не отправляются.

---

## 🚀 Быстрый старт для пользователей

### 1. Скачивание и запуск
1. Перейдите в раздел [**Releases**](../../releases) и скачайте архив для вашей системы:
   - **Windows:** `Bubblyzer-Windows-x64.zip`
   - **macOS:** `Bubblyzer-macOS.zip`
2. Распакуйте архив в удобную папку.
3. Запустите `Bubblyzer.exe` (на Windows) или `Bubblyzer.app` (на macOS).
4. В системном трее появится иконка 💬, а вы получите уведомление о готовности сервера к работе.

---

### 2. Запуск сканирования в Affinity
1. Откройте проект комикса в **Affinity by Canva**.
2. Установите скрипт `affinity_bubblyzer.js` с помощью [**Script Manager for Affinity**](https://jirikrblich.github.io/Affinity-script-manager/).
3. Запустите скрипт — в появившемся диалоговом окне настройте порог и нажмите **ОК**. Нейросеть автоматически найдет пузыри и расставит текстовые фреймы!

---

## 🛠️ Запуск из исходного кода (для разработчиков)

### Требования
- Python 3.10+
- `pip`

### Установка
```bash
# Клонируйте репозиторий
git clone https://github.com/BATCOM/Bubblyzer.git
cd Bubblyzer

# Установите зависимости
pip install -r requirements.txt

# Экспортируйте/скачайте ONNX модель
python export_onnx.py

# Запустите приложение в режиме трея
python main.py

# Или в консольном режиме для отладки
python main.py --cli
```

### Сборка standalone `.exe` (Windows)
```bat
build_windows.bat
```
Собранный исполняемый файл появится в папке `dist/Bubblyzer.exe`.

---

## 📡 REST API сервера

Локальный сервер Bubblyzer работает по адресу `http://127.0.0.1:5000`:

| Эндпоинт | Метод | Описание |
|---|---|---|
| `/` | `GET` | Красивая панель статуса в веб-браузере |
| `/status` | `GET` | JSON со статусом сервера и активным ускорителем (`DirectML`, `CoreML`, `CPU`) |
| `/detect` | `GET` / `POST` | Распознавание бабблов на изображении (`image_path=...`, `cleanup=true`) |
| `/config` | `GET` / `POST` | Чтение и сохранение настроек сканирования |

---

## 📜 Лицензия и благодарности

- Исходный код Bubblyzer распространяется под лицензией **MIT** (см. файл [LICENSE](LICENSE)).
- Веса базовой модели детекции бабблов предоставлены исследователем **ogkalu** ([Hugging Face Model Card](https://huggingface.co/ogkalu/comic-speech-bubble-detector-yolov8m)).
- Разработано командой [**BATCOM**](https://boosty.to/nananabatcom).
