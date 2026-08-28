# 💬 Bubblyzer by BATCOM

[![Release](https://img.shields.io/github/v/release/BATCOM/Bubblyzer?style=flat-square&color=a7f175)](https://github.com)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue?style=flat-square)](https://github.com)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-ONNX%20Runtime%20%2B%20DirectML-success?style=flat-square)](https://onnxruntime.ai/)
[![Integration](https://img.shields.io/badge/Affinity-Publisher%20%26%20Designer%20v2-orange?style=flat-square)](https://affinity.serif.com/)

**Bubblyzer by BATCOM** — это умный инструмент на базе искусственного интеллекта (**YOLOv8 ONNX**) для автоматического поиска диалоговых пузырей (бабблов) на страницах комиксов и манги с мгновенной расстановкой текстовых фреймов в **Affinity by Canva** (Publisher и Designer).

---

## ✨ Возможности

- **⚡ Высокая скорость и легкость:** Работает на оптимизированном движке ONNX Runtime, запускается мгновенно и не требует тяжелых библиотек.
- **🚀 Аппаратное ускорение из коробки:**
  - **Windows:** `DirectML` (работает на **любых** видеокартах: NVIDIA, AMD Radeon, Intel Arc / UHD).
  - **macOS:** `CoreML` (полная поддержка процессоров Apple Silicon M1 / M2 / M3 / M4 и Neural Engine).
  - **Автоматический откат на CPU:** если видеокарта не обнаружена, приложение продолжит работать на процессоре.
- **🎨 Полная интеграция с Affinity by Canva:** Скрипт `affinity_bubblyzer.js` сканирует страницы и создает текстовые блоки (`Frame Text`) точного размера прямо поверх найденных бабблов.
- **🌐 Двуязычный интерфейс:** Полная поддержка **русского** и **английского** языков в окне настроек Affinity и веб-панели.
- **🔒 100% Конфиденциально и офлайн:** Все изображения обрабатываются локально на вашем компьютере, данные никуда не отправляются.
- **☕ Тихий режим:** Приложение аккуратно сворачивается в системный трей рядом с часами и не мешает работе.

---

## 🚀 Как использовать

### Шаг 1. Скачайте и запустите Bubblyzer
1. Перейдите в раздел [**Releases**](../../releases) и скачайте архив для вашей операционной системы:
   - **Windows:** `Bubblyzer-Windows-x64.zip`
   - **macOS:** `Bubblyzer-macOS.zip`
2. Распакуйте архив в любое удобное место.
3. Запустите `Bubblyzer.exe` (на Windows) или `Bubblyzer.app` (на macOS).
4. В системном трее появится иконка 💬 — сервер готов к работе.

---

### Шаг 2. Запустите сканирование в Affinity
1. Откройте проект комикса в **Affinity by Canva**.
2. Установите скрипт `affinity_bubblyzer.js` с помощью бесплатного менеджера скриптов [**Script Manager for Affinity**](https://jirikrblich.github.io/Affinity-script-manager/).
3. Нажмите кнопку запуска скрипта в Affinity.
4. В появившемся окне выберите диапазон страниц, настройте порог уверенности и нажмите **OK**.
5. Нейросеть автоматически найдет все бабблы и расставит готовые текстовые фреймы!

---

## 📜 Лицензия и благодарности

- Исходный код Bubblyzer распространяется под лицензией **MIT** (см. файл [LICENSE](LICENSE)).
- Веса базовой модели детекции бабблов предоставлены исследователем **ogkalu** ([Hugging Face](https://huggingface.co/ogkalu/comic-speech-bubble-detector-yolov8m)).
- Разработано командой [**BATCOM**](https://boosty.to/nananabatcom).
