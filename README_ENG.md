<div align="center">

<b><a href="README.md">Русский</a> | English</b>

<img src="./assets/bubblyzer_demo.gif" width="100%">

# 💬 Bubblyzer by BATCOM

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

### Step 1. Initial Affinity by Canva Setup (One-time)
1. **Enable MCP Server:** navigate to `Edit → Settings → Model Context Protocol` and check **Enable Affinity MCP**.
2. **Open Scripts Panel:** navigate to `Window → General → Scripts` and create any category if none exists yet (e.g. *My Scripts*).
3. **Restart Affinity by Canva** so the MCP server settings take effect.

---

### Step 2. Launch Bubblyzer & Install Script
1. Go to the [**Releases**](../../releases) page and download the archive for your operating system:
   - **Windows:** `Bubblyzer-Windows-x64.zip` *(Windows 10/11 64-bit)*
   - **macOS:** `Bubblyzer-macOS.zip` *(macOS 12+ Apple Silicon & Intel)*
2. Extract the archive and launch `Bubblyzer.exe` (on Windows) or `Bubblyzer.app` (on macOS).
   > **💡 Launch Notes:**
   > - **Windows:** On fresh systems, if you encounter a missing DLL error, install official [Microsoft Visual C++ 2015-2022 Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe). If Windows SmartScreen displays a warning, click *“More info” ➡️ “Run anyway”*.
   > - **macOS:** Since the application is distributed as free open-source software without a paid Apple Developer certificate, Gatekeeper may show an untrusted developer prompt on first launch. Right-click `Bubblyzer.app` ➡️ select **“Open”** (or clear the quarantine attribute in Terminal via `xattr -cr /path/to/Bubblyzer.app`).
3. The <img src="./assets/tray_icon.png" style="height: 17px; vertical-align: middle;"> icon will appear in your system tray. Click it (or open [**http://127.0.0.1:28734**](http://127.0.0.1:28734) in your browser) and click **"Install script into Affinity"**.
   *(The script will be registered automatically via Affinity's MCP bridge. You can also install it manually via [Script Manager for Affinity](https://jirikrblich.github.io/Affinity-script-manager/)).*

---

### Step 3. Run Bubble Detection in Affinity
1. Open your comic project in **Affinity by Canva**.
2. In the **Scripts** panel, click the **Bubblyzer by BATCOM** script.
3. In the dialog, select your target page range, adjust the confidence threshold, and click **OK**.
4. The AI will detect all speech bubbles and automatically create ready-to-type text frames!

> **💡 Tip:** For everyday workflow, simply keep Bubblyzer running in the tray and launch the script directly from Affinity!

---

## 📜 License & Credits

- Bubblyzer source code is distributed under the **MIT License** (see [LICENSE](LICENSE)).
- Base speech bubble detection model weights provided by researcher **ogkalu** ([Hugging Face](https://huggingface.co/ogkalu/comic-speech-bubble-detector-yolov8m)).
- Created by the [**BATCOM**](https://nananabat.com) team • [Support on Boosty](https://boosty.to/nananabatcom).
