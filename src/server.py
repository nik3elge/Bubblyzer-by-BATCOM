import os
import sys
import json
import base64
import logging
from flask import Flask, request, jsonify, render_template_string
from version import __version__, __app_name__, __author__, __boosty_url__, DEFAULT_PORT, DEFAULT_HOST, DEFAULT_SERVER_URL

app = Flask(__name__)
# Suppress default flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

processor_instance = None
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = getattr(sys, '_MEIPASS', ROOT_DIR)

def get_user_config_path():
    """Get standard OS user configuration path for Bubblyzer."""
    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA") or os.path.expanduser("~")
        cfg_dir = os.path.join(app_data, "Bubblyzer")
    elif sys.platform == "darwin":
        cfg_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Bubblyzer")
    else:
        cfg_dir = os.path.join(os.path.expanduser("~"), ".config", "bubblyzer")
    
    try:
        os.makedirs(cfg_dir, exist_ok=True)
    except Exception:
        pass
    
    return os.path.join(cfg_dir, "config.json")

def get_icon_base64():
    """Retrieve base64 data URI of the app icon."""
    search_dirs = [
        os.path.join(BASE_DIR, "assets"),
        BASE_DIR,
        os.path.join(ROOT_DIR, "assets"),
        os.path.join(os.getcwd(), "assets"),
        os.getcwd()
    ]
    for sdir in search_dirs:
        for fn, mime in [('app_icon.svg', 'image/svg+xml'), ('app_icon_clear.svg', 'image/svg+xml'), ('app_icon.png', 'image/png')]:
            path = os.path.join(sdir, fn)
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        encoded = base64.b64encode(f.read()).decode('utf-8')
                        return f"data:{mime};base64,{encoded}"
                except Exception:
                    pass
    return ""

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }} v{{ version }} by {{ author }}</title>
    {% if icon_data %}
    <link rel="icon" href="{{ icon_data }}">
    {% endif %}
    <style>
        :root {
            --bg: #0e1318;
            --card-bg: #161e27;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #a7f175;
            --accent-glow: rgba(167, 241, 117, 0.25);
            --success: #a7f175;
            --border: #233140;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 20px; padding: 32px; max-width: 600px; width: 100%; box-shadow: 0 15px 35px -5px rgba(0,0,0,0.6); }
        .header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }
        .logo-img { width: 56px; height: 56px; border-radius: 14px; box-shadow: 0 0 20px var(--accent-glow); object-fit: contain; }
        .logo-placeholder { width: 56px; height: 56px; background: #a7f175; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 28px; box-shadow: 0 0 20px var(--accent-glow); }
        .title h1 { font-size: 22px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px; }
        .title h1 span.ver { font-size: 13px; font-weight: 600; color: #0e1318; background: var(--accent); padding: 2px 8px; border-radius: 6px; }
        .title p { font-size: 13px; color: var(--accent); letter-spacing: 0.5px; text-transform: uppercase; font-weight: 600; margin-top: 2px; }
        .status-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(167, 241, 117, 0.1); border: 1px solid rgba(167, 241, 117, 0.3); color: var(--success); padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 20px; }
        .status-dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; box-shadow: 0 0 8px var(--success); }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
        .info-box { background: rgba(14, 19, 24, 0.7); border: 1px solid var(--border); border-radius: 12px; padding: 14px; }
        .info-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; }
        .info-val { font-size: 15px; font-weight: 600; color: #fff; }
        .instructions { background: rgba(167, 241, 117, 0.04); border: 1px dashed rgba(167, 241, 117, 0.3); border-radius: 12px; padding: 16px; font-size: 13px; line-height: 1.6; color: var(--text-muted); }
        .instructions b { color: #fff; }
        .footer { margin-top: 24px; text-align: center; font-size: 12px; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 16px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            {% if icon_data %}
            <img src="{{ icon_data }}" alt="Logo" class="logo-img">
            {% else %}
            <div class="logo-placeholder">💬</div>
            {% endif %}
            <div class="title">
                <h1>{{ app_name }} <span class="ver">v{{ version }}</span></h1>
                <p>by {{ author }}</p>
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
            <a href="{{ boosty_url }}" target="_blank" style="color: var(--accent); text-decoration: none; font-weight: 600;">{{ app_name }} v{{ version }} by {{ author }}</a> &bull; Модель YOLOv8 ONNX (автор базы: ogkalu)
        </div>
    </div>
</body>
</html>
"""

def load_config():
    user_cfg_path = get_user_config_path()
    if os.path.exists(user_cfg_path):
        try:
            with open(user_cfg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback to local config if present
    local_cfg_path = os.path.join(ROOT_DIR, "config.json")
    if os.path.exists(local_cfg_path):
        try:
            with open(local_cfg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"confidence": 40, "group_frames": True, "mode": 0, "pages": "", "lang": "ru"}

def save_config(cfg):
    user_cfg_path = get_user_config_path()
    try:
        with open(user_cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")

@app.route('/')
def index():
    accelerator = processor_instance.active_provider if processor_instance else "Unknown"
    icon_data = get_icon_base64()
    return render_template_string(
        HTML_DASHBOARD,
        accelerator=accelerator,
        port=DEFAULT_PORT,
        version=__version__,
        app_name=__app_name__,
        author=__author__,
        boosty_url=__boosty_url__,
        icon_data=icon_data
    )

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "name": f"{__app_name__} by {__author__}",
        "version": __version__,
        "port": DEFAULT_PORT,
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
            if 'lang' in request.args:
                cfg['lang'] = request.args.get('lang')
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

def start_server(processor, port=DEFAULT_PORT):
    global processor_instance
    processor_instance = processor
    app.run(host=DEFAULT_HOST, port=port, debug=False, use_reloader=False)
