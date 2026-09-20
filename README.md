<div align="center">

<b>Русский | <a href="README_ENG.md">English</a></b>

<img src="./assets/bubblyzer_demo.gif" width="100%">

# Bubblyzer от BATCOM

[![Release](https://img.shields.io/github/v/release/nik3elge/Bubblyzer-by-BATCOM?style=flat-square&color=a7f175)](https://github.com/nik3elge/Bubblyzer-by-BATCOM/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue?style=flat-square)](https://github.com/nik3elge/Bubblyzer-by-BATCOM/releases)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-ONNX%20Runtime%20%2B%20DirectML-success?style=flat-square)](https://onnxruntime.ai/)
[![Affinity by Canva](https://img.shields.io/badge/Affinity%20by%20Canva-Mid%20Sept%20%2726%20(4850)-bbee81?style=flat-square)](https://affinity.serif.com/)
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
- **🎨 Полная интеграция с Affinity by Canva:** Официальный пакет скрипта `Bubblyzer.afscript` сканирует страницы и создаёт текстовые блоки (`Frame Text`) точного размера прямо поверх найденных бабблов.
- **🔒 100% Конфиденциально и офлайн:** Все изображения обрабатываются локально на вашем компьютере, данные никуда не отправляются.
- **☕ Тихий режим:** Приложение аккуратно сворачивается в системный трей рядом с часами и не мешает работе.

---

## 🚀 Как использовать

### Шаг 1. Первичная настройка безопасности в Affinity (выполняется 1 раз)
1. В меню Affinity перейдите в `Edit → Settings → Scripting` (на macOS: `Affinity → Settings → Scripting`).
2. Включите переключатель **Enable Affinity Scripting**.
3. В блоке **Default Permissions** (Разрешения по умолчанию) включите:
   - ☑ **Access the file system** (доступ к диску для временного экспорта страниц)
   - ☑ **Access networks** (доступ к сети для связи с локальной нейросетью Bubblyzer)
4. В блоке **File System access** нажмите кнопку **`Add`** (Добавить) и укажите папку **Desktop** (Рабочий стол). Именно на Рабочий стол скрипт временно экспортирует превью страниц для передачи в нейросеть (при желании можно также добавить вашу рабочую папку с проектами).

---

### Шаг 2. Запуск Bubblyzer и установка скрипта
1. Перейдите в раздел [**Releases**](../../releases) и скачайте архив для вашей системы:
   - **Windows:** `Bubblyzer-Windows-x64.zip` *(Windows 10/11 64-bit)*
   - **macOS:** `Bubblyzer-macOS.zip` *(macOS 12+ Apple Silicon & Intel)*
2. Распакуйте архив и запустите `Bubblyzer.exe` (на Windows) или `Bubblyzer.app` (на macOS).
   > **💡 Примечания по запуску:**
   > - **Windows:** Если система новая и выдает ошибку о недостающей DLL, установите стандартный [Microsoft Visual C++ 2015-2022 Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe). При предупреждении SmartScreen нажмите *«Подробнее» ➡️ «Выполнить в любом случае»*.
   > - **macOS:** Так как приложение распространяется бесплатно без платной подписи Apple Developer, при первом открытии может появиться предупреждение Gatekeeper. Нажмите правой кнопкой мыши по `Bubblyzer.app` ➡️ выберите **«Открыть»** (или снимите карантин командой в Терминале: `xattr -cr /путь/к/Bubblyzer.app`).
3. **Импортируйте скрипт в Affinity:**
   - В меню Affinity откройте `Window → Scripting → Scripts Library` (Окно → Скриптинг → Библиотека скриптов).
   - В строке нужной категории (например, **Default**) нажмите **значок меню справа** (иконка списка `:=`) и выберите **Import Script...** ➔ укажите файл `Bubblyzer.afscript` из распакованной папки с программой.
   > **💡 Подсказка:** Верхнее меню в заголовке панели (`v`) содержит пункт «Import Scripts...» для целых пакетов категорий (`.afscripts`), а импорт одиночного скрипта («Import Script...») находится именно в меню самой категории.
4. **Сделайте скрипт доверенным (Affinity Security):**
   - В панели **Scripts Library** нажмите правой кнопкой мыши по установленному скрипту **Bubblyzer by BATCOM** и выберите **Mark as Trusted** (Сделать доверенным).

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
