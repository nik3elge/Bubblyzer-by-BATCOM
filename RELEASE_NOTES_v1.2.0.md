# 🚀 Релиз Bubblyzer v1.2.0

### 🎯 Главная причина обновления
Ключевым поводом для выпуска версии **1.2.0** стал долгожданный релиз новой версии графического редактора **Affinity by Canva (Mid Sept '26, сборка 4850)**, в которой разработчики официально представили **полноценную нативную систему скриптинга и библиотеку скриптов (`.afscript`)**. 

Благодаря этому отпала необходимость в использовании громоздких внешних мостов и протоколов управления — интеграция Bubblyzer с Affinity теперь стала бесшовной, быстрой и нативной.

### 🌟 Что изменилось:
- **Удалён слой MCP (Model Context Protocol)**: зависимость от дополнительного MCP-сервера и сторонних мостов полностью устранена.
- **Новый нативный формат `.afscript`**: код упакован в официальный контейнер Serif с метаданными и устанавливается в один клик через встроенную панель (`Window → Scripting → Scripts Library` ➔ **Import Script...**).
- **Прямой JavaScript API Affinity**: экспорт страниц и расстановка текстовых рамок теперь выполняются напрямую через движок Affinity с поддержкой истории отмены (`Ctrl+Z`).
- **Адаптация к песочнице безопасности**: добавлена поддержка строгих разрешений Affinity (экспорт превью через `Desktop` и режим `Mark as Trusted`).
- **Чистый дистрибутив**: в архиве релиза теперь только два файла — приложение (`Bubblyzer.exe` или `Bubblyzer.app`) и нативный скрипт `Bubblyzer.afscript`.

---

# 🚀 Bubblyzer v1.2.0 Release

### 🎯 Key Reason for the Update
The primary driver for version **1.2.0** is the long-awaited release of the updated **Affinity by Canva (Mid Sept '26, build 4850)**, in which Serif officially introduced **native scripting support and the Scripts Library (`.afscript`)**.

This eliminates the need for cumbersome external bridges and protocols — Bubblyzer’s integration with Affinity is now seamless, fast, and fully native.

### 🌟 What's Changed:
- **Removed MCP (Model Context Protocol) Layer**: Dependency on external MCP servers and bridge processes has been completely eliminated.
- **New Native `.afscript` Format**: Script is packaged into the official Serif container with metadata, installable in one click via the built-in panel (`Window → Scripting → Scripts Library` ➔ **Import Script...**).
- **Direct Affinity JavaScript API**: Page rendering and text frame placement now run directly through Affinity’s internal engine with full Undo/Redo (`Ctrl+Z`) support.
- **Security Sandbox Adaptation**: Added support for Affinity's strict permissions (temporary preview export via `Desktop` and `Mark as Trusted` status).
- **Clean Distribution**: Release archives now contain just two files — the application (`Bubblyzer.exe` or `Bubblyzer.app`) and the native script `Bubblyzer.afscript`.