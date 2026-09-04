<div align="center">

<b>Русский | <a href="README_ENG.md">English</a></b>

<img src="./assets/bubblyzer_demo.gif" width="100%">

# Bubblyzer от [BATCOM](https://nananabat.com)

[![Release](https://img.shields.io/github/v/release/nik3elge/Bubblyzer-by-BATCOM?style=flat-square&color=a7f175)](https://github.com/nik3elge/Bubblyzer-by-BATCOM/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue?style=flat-square)](https://github.com/nik3elge/Bubblyzer-by-BATCOM/releases)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-ONNX%20Runtime%20%2B%20DirectML-success?style=flat-square)](https://onnxruntime.ai/)
[![Integration](https://img.shields.io/badge/Affinity-by%20Canva-bbee81?style=flat-square)](https://affinity.serif.com/)
[![Boosty](https://img.shields.io/badge/Boosty-BATCOM-orange?style=flat-square&logo=boosty&logoColor=white)](https://boosty.to/nananabatcom)

**Умный инструмент на базе ИИ (YOLOv8 ONNX) для автоматического поиска диалоговых пузырей (бабблов) на страницах комиксов и манги с мгновенной расстановкой текстовых фреймов в Affinity by Canva.**

</div>

---

## ✨ Возможности

- **⚡ Высокая скорость и лёгкость:** Работает на оптимизированном движке ONNX Runtime, запускается мгновенно и не требует тяжёлых библиотек.
- **🚀 Аппаратное ускорение из коробки:**
  - **Windows:** `DirectML` (работает на **любых** видеокартах: NVIDIA, AMD Radeon, Intel Arc / UHD).
  - **macOS:** `CoreML` (полная поддержка процессоров Apple Silicon M1 / M2 / M3 / M4 и Neural Engine).
  - **Автоматический откат на CPU:** если видеокарта не обнаружена, приложение продолжит работать на процессоре.
- **🎨 Полная интеграция с Affinity by Canva:** Скрипт `affinity_bubblyzer.js` сканирует страницы и создаёт текстовые блоки (`Frame Text`) точного размера прямо поверх найденных бабблов.
- **🔒 100% Конфиденциально и офлайн:** Все изображения обрабатываются локально на вашем компьютере, данные никуда не отправляются.
- **☕ Тихий режим:** Приложение аккуратно сворачивается в системный трей рядом с часами и не мешает работе.

---

## 🚀 Как использовать

### Шаг 1. Скачайте и запустите Bubblyzer
1. Перейдите в раздел [**Releases**](../../releases) и скачайте архив для вашей операционной системы:
   - **Windows:** `Bubblyzer-Windows-x64.zip`
   - **macOS:** `Bubblyzer-macOS.zip`
2. Распакуйте архив в любое удобное место.
3. Запустите `Bubblyzer.exe` (на Windows) или `Bubblyzer.app` (на macOS).
4. В системном трее появится иконка <img src="./assets/tray_icon.png" style="height: 17px; vertical-align: middle;"> — локальный ИИ-сервер готов к работе на порту `28734`.
5. *(Опционально)* Кликните по иконке в трее или откройте в браузере [**http://127.0.0.1:28734**](http://127.0.0.1:28734), чтобы посмотреть статус готовности сервера, активный видеоускоритель (DirectML / CoreML / CPU) и веб-панель.

---

### Шаг 2. Настройте Affinity и запустите сканирование
1. **Требования в Affinity (выполняется один раз):**
   - Включите MCP-сервер: перейдите в меню `Edit → Settings → Model Context Protocol` и включите **Enable Affinity MCP** (*после включения обязательно перезапустите Affinity!*).
   - Откройте панель скриптов: перейдите в меню `Window → General → Scripts` и создайте в ней любую категорию, если ее нет (например, *My Scripts*).
2. Откройте проект комикса в **Affinity by Canva**.
3. В веб-панели Bubblyzer ([**http://127.0.0.1:28734**](http://127.0.0.1:28734)) нажмите **«Установить скрипт в Affinity»** (скрипт установится автоматически через встроенный MCP-мост Affinity). Также можно установить вручную через [**Script Manager for Affinity**](https://jirikrblich.github.io/Affinity-script-manager/).
4. Запустите скрипт кликом по нему в панели **Scripts** в Affinity.
5. В появившемся окне выберите диапазон страниц, настройте порог уверенности и нажмите **OK**.
6. Нейросеть автоматически найдёт все бабблы и расставит готовые текстовые фреймы!

---

## 📜 Лицензия и благодарности

- Исходный код Bubblyzer распространяется под лицензией **MIT** (см. файл [LICENSE](LICENSE)).
- Веса базовой модели детекции бабблов предоставлены исследователем **ogkalu** ([Hugging Face](https://huggingface.co/ogkalu/comic-speech-bubble-detector-yolov8m)).
- Разработано командой [**BATCOM**](https://nananabat.com) • [Поддержать на Boosty](https://boosty.to/nananabatcom).
