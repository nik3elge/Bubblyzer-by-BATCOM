<div align="center">

<b><a href="README.md">Русский</a> | English</b>

<img src="./assets/bubblyzer_demo.gif" width="100%">

# 💬 Bubblyzer by BATCOM

[![Release](https://img.shields.io/github/v/release/nik3elge/Bubblyzer-by-BATCOM?style=flat-square&color=a7f175)](https://github.com/nik3elge/Bubblyzer-by-BATCOM/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue?style=flat-square)](https://github.com/nik3elge/Bubblyzer-by-BATCOM/releases)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-ONNX%20Runtime%20%2B%20DirectML-success?style=flat-square)](https://onnxruntime.ai/)
[![Affinity by Canva](https://img.shields.io/badge/Affinity%20by%20Canva-Mid%20Sept%20%2726%20(4850)-bbee81?style=flat-square)](https://affinity.serif.com/)
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
- **🎨 Native Integration with Affinity by Canva:** The official `Bubblyzer.afscript` package scans your pages and generates precise `Frame Text` nodes directly over detected speech bubbles.
- **🌐 Bilingual UI:** Full support for both **English** and **Russian** languages in the Affinity dialog and local web dashboard.
- **🔒 100% Private & Offline:** All image processing runs locally on your machine. No telemetry, no cloud uploads.
- **☕ Quiet Tray Mode:** Sits quietly in your system tray without interrupting your creative workflow.

---

## 🚀 How to Use

### Step 1. Initial Affinity by Canva Setup (One-time)
1. In Affinity, navigate to `Edit → Settings → Scripting` (on macOS: `Affinity → Settings → Scripting`).
2. Check **Enable Affinity Scripting**.
3. Under **Default Permissions**, enable:
   - ☑ **Access the file system** (disk access for temporary page previews)
   - ☑ **Access networks** (local network access to communicate with the Bubblyzer AI server)
4. Under **File System access**, click **`Add`** and add your **Desktop** folder. The script temporarily exports page previews to Desktop to send them to the AI (optionally, you can also add your project folder).

---

### Step 2. Launch Bubblyzer & Install Script
1. Go to the [**Releases**](../../releases) page and download the archive for your operating system:
   - **Windows:** `Bubblyzer-Windows-x64.zip` *(Windows 10/11 64-bit)*
   - **macOS:** `Bubblyzer-macOS.zip` *(macOS 12+ Apple Silicon & Intel)*
2. Extract the archive and launch `Bubblyzer.exe` (on Windows) or `Bubblyzer.app` (on macOS).
   > **💡 Launch Notes:**
   > - **Windows:** On fresh systems, if you encounter a missing DLL error, install official [Microsoft Visual C++ 2015-2022 Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe). If Windows SmartScreen displays a warning, click *“More info” ➡️ “Run anyway”*.
   > - **macOS:** Since the application is distributed as free open-source software without a paid Apple Developer certificate, Gatekeeper may show an untrusted developer prompt on first launch. Right-click `Bubblyzer.app` ➡️ select **“Open”** (or clear the quarantine attribute in Terminal via `xattr -cr /path/to/Bubblyzer.app`).
3. **Import Script into Affinity:**
   - In Affinity, open `Window → Scripting → Scripts Library`.
   - On your target category row (e.g. **Default**), click the **menu icon on the right** (list icon `:=`) and select **Import Script...** ➔ choose `Bubblyzer.afscript` from the unpacked application folder.
   > **💡 Tip:** The top panel header menu (`v`) contains "Import Scripts..." for entire category archives (`.afscripts`), whereas importing a single script ("Import Script...") is found specifically in the category's own menu.
4. **Mark Script as Trusted (Affinity Security):**
   - In the **Scripts Library** panel, right-click the installed **Bubblyzer by BATCOM** script and select **Mark as Trusted**.

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
