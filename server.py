import os
import sys
import json
import logging
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
# Suppress default flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

processor_instance = None
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bubblyzer by BATCOM</title>
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.2);
            --success: #4ade80;
            --border: #334155;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; padding: 32px; max-width: 600px; width: 100%; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }
        .header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }
        .logo { width: 48px; height: 48px; background: linear-gradient(135deg, #38bdf8, #818cf8); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: white; box-shadow: 0 0 15px var(--accent-glow); }
        .title h1 { font-size: 22px; font-weight: 700; color: #fff; }
        .title p { font-size: 13px; color: var(--accent); letter-spacing: 0.5px; text-transform: uppercase; font-weight: 600; }
        .status-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(74, 222, 128, 0.1); border: 1px solid rgba(74, 222, 128, 0.3); color: var(--success); padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 20px; }
        .status-dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; box-shadow: 0 0 8px var(--success); }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
        .info-box { background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border); border-radius: 10px; padding: 14px; }
        .info-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; }
        .info-val { font-size: 15px; font-weight: 600; color: #fff; }
        .instructions { background: rgba(56, 189, 248, 0.05); border: 1px dashed rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 16px; font-size: 13px; line-height: 1.6; color: var(--text-muted); }
        .instructions b { color: #fff; }
        .footer { margin-top: 24px; text-align: center; font-size: 12px; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 16px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="logo">💬</div>
            <div class="title">
                <h1>Bubblyzer</h1>
                <p>by BATCOM</p>
            </div>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            Локальный сервер активен и готов к работе
        </div>
        <div class="grid">
            <div class="info-box">
                <div class="info-label">Аппаратный ускоритель</div>
                <div class="info-val">⚡ {{ accelerator }}</div>
            </div>
            <div class="info-box">
                <div class="info-label">Порт API</div>
                <div class="info-val">http://127.0.0.1:{{ port }}</div>
            </div>
        </div>
        <div class="instructions">
            <b>Как использовать:</b>
            <ol style="margin-left: 20px; margin-top: 8px;">
                <li>Откройте проект комикса в <b>Affinity by Canva</b>.</li>
                <li>Установите скрипт <code>affinity_bubblyzer.js</code> с помощью <a href="https://jirikrblich.github.io/Affinity-script-manager/" target="_blank" style="color: var(--accent); text-decoration: underline;">Script Manager for Affinity</a>.</li>
                <li>Запустите скрипт и нейросеть автоматически найдет пузыри и расставит текстовые фреймы!</li>
            </ol>
        </div>
        <div class="footer">
            <a href="https://boosty.to/nananabatcom" target="_blank" style="color: var(--accent); text-decoration: none; font-weight: 600;">Bubblyzer by BATCOM</a> &bull; Модель YOLOv8 ONNX (автор базы: ogkalu)
        </div>
    </div>
</body>
</html>
"""

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"confidence": 40, "group_frames": True, "mode": 0, "pages": ""}

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")

@app.route('/')
def index():
    accelerator = processor_instance.active_provider if processor_instance else "Unknown"
    return render_template_string(HTML_DASHBOARD, accelerator=accelerator, port=5000)

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "name": "Bubblyzer by BATCOM",
        "version": "1.0.0",
        "status": "ready",
        "accelerator": processor_instance.active_provider if processor_instance else "None",
        "model_loaded": processor_instance is not None and processor_instance.session is not None
    })

@app.route('/config', methods=['GET', 'POST'])
def config_endpoint():
    if request.method == 'POST' or request.args.get('save') == '1':
        cfg = load_config()
        if request.is_json and request.json:
            cfg.update(request.json)
        else:
            if 'confidence' in request.args:
                try: cfg['confidence'] = int(request.args.get('confidence'))
                except ValueError: pass
            if 'group_frames' in request.args:
                cfg['group_frames'] = request.args.get('group_frames').lower() in ('true', '1', 'yes')
            if 'mode' in request.args:
                try: cfg['mode'] = int(request.args.get('mode'))
                except ValueError: pass
            if 'pages' in request.args:
                cfg['pages'] = request.args.get('pages')
        save_config(cfg)
        return jsonify(cfg)
    else:
        return jsonify(load_config())

@app.route('/detect', methods=['POST', 'GET'])
def detect():
    if request.method == 'GET':
        img_path = request.args.get('image_path')
        clean_up = request.args.get('cleanup', 'false').lower() in ('true', '1', 'yes')
        conf = float(request.args.get('confidence', 0.20))
    else:
        data = request.json or {}
        img_path = data.get('image_path')
        clean_up = bool(data.get('cleanup', False))
        conf = float(data.get('confidence', 0.20))

    if not img_path:
        return jsonify({"error": "Missing image_path"}), 400
    if not processor_instance:
        return jsonify({"error": "Processor not initialized"}), 500

    try:
        file_results = processor_instance.detect(img_path, conf_threshold=conf)
        
        if clean_up:
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception as err:
                print(f"Cleanup warning: {err}")

        return jsonify(file_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def start_server(processor, port=5000):
    global processor_instance
    processor_instance = processor
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
