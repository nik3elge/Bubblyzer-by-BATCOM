<div align="center">

<b>Русский | <a href="README_ENG.md">English</a></b>

<img src="./assets/bubblyzer_demo.gif" width="100%">

# Bubblyzer от BATCOM

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

### Шаг 1. Первичная настройка Affinity by Canva (выполняется 1 раз)
1. **Включите MCP-сервер:** перейдите в меню `Edit → Settings → Model Context Protocol` и включите **Enable Affinity MCP** (*после включения обязательно перезапустите Affinity!*).
2. **Откройте панель скриптов:** перейдите в меню `Window → General → Scripts` и создайте в ней любую категорию, если ее еще нет (например, *My Scripts*).

---

### Шаг 2. Запуск Bubblyzer и установка скрипта
1. Перейдите в раздел [**Releases**](../../releases) и скачайте архив для вашей системы:
   - **Windows:** `Bubblyzer-Windows-x64.zip` *(Windows 10/11 64-bit)*
   - **macOS:** `Bubblyzer-macOS.zip` *(macOS 12+ Apple Silicon & Intel)*
2. Распакуйте архив и запустите `Bubblyzer.exe` (на Windows) или `Bubblyzer.app` (на macOS).
   > **💡 Примечания по запуску:**
   > - **Windows:** Если система новая и выдает ошибку о недостающей DLL, установите стандартный [Microsoft Visual C++ 2015-2022 Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe). При предупреждении SmartScreen нажмите *«Подробнее» ➡️ «Выполнить в любом случае»*.
   > - **macOS:** Так как приложение распространяется бесплатно без платной подписи Apple Developer, при первом открытии может появиться предупреждение Gatekeeper. Нажмите правой кнопкой мыши по `Bubblyzer.app` ➡️ выберите **«Открыть»** (или снимите карантин командой в Терминале: `xattr -cr /путь/к/Bubblyzer.app`).
3. В системном трее появится иконка <img src="./assets/tray_icon.png" style="height: 17px; vertical-align: middle;">. Кликните по ней (или перейдите в браузере на [**http://127.0.0.1:28734**](http://127.0.0.1:28734)) и нажмите **«Установить скрипт в Affinity»**.
   *(Скрипт автоматически добавится в Affinity через встроенный MCP-мост. Также скрипт можно установить вручную через [Script Manager for Affinity](https://jirikrblich.github.io/Affinity-script-manager/)).*

---

### Шаг 3. Распознавание бабблов в Affinity
1. Откройте проект комикса в **Affinity by Canva**.
2. В панели **Scripts** нажмите на скрипт **Bubblyzer by BATCOM**.
3. В появившемся окне выберите диапазон страниц, настройте порог уверенности и нажмите **OK**.
4. Нейросеть автоматически найдёт все бабблы и расставит готовые текстовые фреймы!

> **💡 Подсказка:** В дальнейшем для работы достаточно просто запустить Bubblyzer и вызывать скрипт прямо из Affinity!

---

## 📜 Лицензия и благодарности

- Исходный код Bubblyzer распространяется под лицензией **MIT** (см. файл [LICENSE](LICENSE)).
- Веса базовой модели детекции бабблов предоставлены исследователем **ogkalu** ([Hugging Face](https://huggingface.co/ogkalu/comic-speech-bubble-detector-yolov8m)).
- Разработано командой [**BATCOM**](https://nananabat.com) • [Поддержать на Boosty](https://boosty.to/nananabatcom).
