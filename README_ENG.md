<div align="center">

<b><a href="README.md">Русский</a> | English</b>

<img src="./assets/bubblyzer_demo.gif" width="100%">

# 💬 Bubblyzer by [BATCOM](https://nananabat.com)

[![Release](https://img.shields.io/github/v/release/nik3elge/Bubblyzer-by-BATCOM?style=flat-square&color=a7f175)](https://github.com/nik3elge/Bubblyzer-by-BATCOM/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue?style=flat-square)](https://github.com/nik3elge/Bubblyzer-by-BATCOM/releases)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-ONNX%20Runtime%20%2B%20DirectML-success?style=flat-square)](https://onnxruntime.ai/)
[![Integration](https://img.shields.io/badge/Affinity-by%20Canva-bbee81?style=flat-square)](https://affinity.serif.com/)
[![Boosty](https://img.shields.io/badge/Boosty-BATCOM-orange?style=flat-square&logo=boosty&logoColor=white)](https://boosty.to/nananabatcom)

**An AI-powered tool (**YOLOv8 ONNX**) for automatic comic and manga speech bubble detection with instant text frame placement in Affinity by Canva.**

</div>

---

## ✨ Features

- **⚡ Fast and Lightweight:** Powered by the optimized ONNX Runtime engine, launching in milliseconds without heavy PyTorch dependencies.
- **🚀 Hardware Acceleration Out of the Box:**
  - **Windows:** `DirectML` (works on **all** GPUs: NVIDIA, AMD Radeon, Intel Arc / UHD).
  - **macOS:** `CoreML` (full support for Apple Silicon M1 / M2 / M3 / M4 and Apple Neural Engine).
  - **Automatic CPU Fallback:** If no GPU is found, seamlessly switches to CPU execution.
- **🎨 Native Integration with Affinity by Canva:** The `affinity_bubblyzer.js` script scans your pages and generates precise `Frame Text` nodes directly over detected speech bubbles.
- **🌐 Bilingual UI:** Full support for both **English** and **Russian** languages in the Affinity dialog and local web dashboard.
- **🔒 100% Private & Offline:** All image processing runs locally on your machine. No telemetry, no cloud uploads.
- **☕ Quiet Tray Mode:** Sits quietly in your system tray without interrupting your creative workflow.

---

## 🚀 How to Use

### Step 1. Download & Launch Bubblyzer
1. Go to the [**Releases**](../../releases) page and download the archive for your operating system:
   - **Windows:** `Bubblyzer-Windows-x64.zip`
   - **macOS:** `Bubblyzer-macOS.zip`
2. Extract the archive to any convenient location.
3. Launch `Bubblyzer.exe` (on Windows) or `Bubblyzer.app` (on macOS).
4. The <img src="./assets/tray_icon.png" style="height: 17px; vertical-align: middle;"> icon will appear in your system tray — the local AI server is ready on port `28734`.
5. *(Optional)* Click the tray icon or open [**http://127.0.0.1:28734**](http://127.0.0.1:28734) in your browser to check server status, active hardware accelerator (DirectML / CoreML / CPU), and the web dashboard.

---

### Step 2. Configure Affinity & Run Bubble Detection
1. **Affinity Setup (one-time requirement):**
   - Enable MCP server: navigate to `Edit → Settings → Model Context Protocol` and check **Enable Affinity MCP** (*restart Affinity after enabling!*).
   - Open Scripts panel: navigate to `Window → General → Scripts` and create any category if none exists (e.g. *My Scripts*).
2. Open your comic project in **Affinity by Canva**.
3. In the Bubblyzer web dashboard ([**http://127.0.0.1:28734**](http://127.0.0.1:28734)), click **"Install script into Affinity"** (the script will be registered automatically via Affinity's built-in MCP bridge). You can also install it via [**Script Manager for Affinity**](https://jirikrblich.github.io/Affinity-script-manager/).
4. Run the script by clicking it in the **Scripts** panel in Affinity.
5. In the dialog, select your target page range, adjust the confidence threshold, and click **OK**.
6. The AI will detect all speech bubbles and automatically create ready-to-type text frames!

---

## 📜 License & Credits

- Bubblyzer source code is distributed under the **MIT License** (see [LICENSE](LICENSE)).
- Base speech bubble detection model weights provided by researcher **ogkalu** ([Hugging Face](https://huggingface.co/ogkalu/comic-speech-bubble-detector-yolov8m)).
- Created by the [**BATCOM**](https://nananabat.com) team • [Support on Boosty](https://boosty.to/nananabatcom).
