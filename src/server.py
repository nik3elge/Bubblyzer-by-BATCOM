import os
import sys
import json
import base64
import logging
from flask import Flask, request, jsonify, render_template_string
from version import __version__, __app_name__, __author__, __author_url__, __boosty_url__, DEFAULT_PORT, DEFAULT_HOST, DEFAULT_SERVER_URL
from affinity_bridge import check_affinity_status, install_bubblyzer_script, execute_bubblyzer_script

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
    <title>{{ app_name }} v{{ version }}</title>
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
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 20px; padding: 32px; max-width: 620px; width: 100%; box-shadow: 0 15px 35px -5px rgba(0,0,0,0.6); }
        .header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }
        .logo-img { width: 56px; height: 56px; border-radius: 14px; box-shadow: 0 0 20px var(--accent-glow); object-fit: contain; }
        .logo-placeholder { width: 56px; height: 56px; background: #a7f175; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 28px; box-shadow: 0 0 20px var(--accent-glow); }
        .title h1 { font-size: 22px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px; }
        .title h1 span.ver { font-size: 13px; font-weight: 600; color: #0e1318; background: var(--accent); padding: 2px 8px; border-radius: 6px; }
        .title p { font-size: 13px; color: var(--accent); letter-spacing: 0.5px; text-transform: uppercase; font-weight: 600; margin-top: 2px; }
        .author-link { color: var(--accent); text-decoration: none; font-weight: 600; transition: all 0.2s ease; }
        .author-link:hover { text-decoration: underline; opacity: 0.85; }
        
        .lang-switcher { margin-left: auto; display: flex; background: rgba(14, 19, 24, 0.9); border: 1px solid var(--border); border-radius: 10px; padding: 3px; gap: 3px; }
        .lang-btn { background: transparent; border: none; color: var(--text-muted); padding: 5px 12px; border-radius: 7px; font-size: 12px; font-weight: 700; cursor: pointer; transition: all 0.2s ease; }
        .lang-btn.active { background: var(--accent); color: #0e1318; box-shadow: 0 0 10px var(--accent-glow); }
        .lang-btn:hover:not(.active) { color: #fff; background: rgba(255, 255, 255, 0.06); }

        .status-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(167, 241, 117, 0.1); border: 1px solid rgba(167, 241, 117, 0.3); color: var(--success); padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 20px; }
        .status-dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; box-shadow: 0 0 8px var(--success); }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
        .info-box { background: rgba(14, 19, 24, 0.7); border: 1px solid var(--border); border-radius: 12px; padding: 14px; }
        .info-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px; font-weight: 600; }
        .info-val { font-size: 15px; font-weight: 600; color: #fff; }

        .affinity-card { background: rgba(167, 241, 117, 0.04); border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; margin-bottom: 20px; }
        .affinity-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 8px; }
        .affinity-title { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #fff; }
        .affinity-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(14, 19, 24, 0.9); border: 1px solid var(--border); padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; color: var(--text-muted); }
        .affinity-dot { width: 7px; height: 7px; border-radius: 50%; background: #64748b; }
        .affinity-dot.connected { background: var(--accent); box-shadow: 0 0 6px var(--accent); }
        .affinity-dot.installed { background: #38bdf8; box-shadow: 0 0 6px #38bdf8; }
        .affinity-desc { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; line-height: 1.5; }
        .affinity-actions { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
        .action-btn { display: inline-flex; align-items: center; gap: 7px; padding: 8px 14px; border-radius: 9px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: 1px solid transparent; }
        .action-btn.primary { background: var(--accent); color: #0e1318; }
        .action-btn.primary:hover:not(:disabled) { box-shadow: 0 0 12px var(--accent-glow); filter: brightness(1.05); }
        .action-btn.secondary { background: rgba(255, 255, 255, 0.08); color: #fff; border-color: var(--border); }
        .action-btn.secondary:hover:not(:disabled) { background: rgba(255, 255, 255, 0.14); border-color: var(--text-muted); }
        .action-btn.icon-btn { padding: 8px 10px; background: rgba(255, 255, 255, 0.05); color: var(--text-muted); border-color: var(--border); }
        .action-btn.icon-btn:hover:not(:disabled) { color: #fff; background: rgba(255, 255, 255, 0.1); }
        .action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .lucide-icon { display: inline-block; vertical-align: middle; flex-shrink: 0; }
        .lucide-icon.spin { animation: lucide-spin 0.8s linear infinite; }
        @keyframes lucide-spin { 100% { transform: rotate(360deg); } }
        .accent-icon { stroke: var(--accent); }

        .affinity-feedback { margin-top: 10px; padding: 8px 12px; border-radius: 8px; font-size: 12px; line-height: 1.4; }
        .affinity-feedback.success { background: rgba(167, 241, 117, 0.12); border: 1px solid rgba(167, 241, 117, 0.3); color: var(--accent); }
        .affinity-feedback.error { background: rgba(248, 113, 113, 0.12); border: 1px solid rgba(248, 113, 113, 0.3); color: #fca5a5; }
        .affinity-feedback.info { background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); color: #7dd3fc; }

        .instructions { background: rgba(167, 241, 117, 0.04); border: 1px dashed rgba(167, 241, 117, 0.3); border-radius: 12px; padding: 18px; font-size: 13px; line-height: 1.6; color: var(--text-muted); }
        .instructions b { color: #fff; }
        .instructions code { background: rgba(255, 255, 255, 0.08); padding: 1px 5px; border-radius: 4px; color: var(--text); font-size: 12px; }

        .boosty-container { margin-top: 20px; display: flex; justify-content: center; }
        .boosty-btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; background: linear-gradient(135deg, #f15f2c 0%, #f33d35 100%); color: #ffffff; text-decoration: none; font-weight: 600; font-size: 13px; padding: 10px 22px; border-radius: 12px; transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease; box-shadow: 0 4px 14px rgba(241, 95, 44, 0.35); }
        .boosty-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(241, 95, 44, 0.5); filter: brightness(1.06); }
        .boosty-btn:active { transform: translateY(0); }
        .boosty-icon { width: 15px; height: 18px; flex-shrink: 0; }

        .footer { margin-top: 20px; text-align: center; font-size: 12px; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 16px; }
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
                <p><span id="t-by-prefix"></span> <a href="{{ author_url }}" target="_blank" class="author-link">{{ author }}</a></p>
            </div>
            <div class="lang-switcher">
                <button class="lang-btn {% if current_lang == 'ru' %}active{% endif %}" id="btn-ru" onclick="setLanguage('ru')">RU</button>
                <button class="lang-btn {% if current_lang == 'en' %}active{% endif %}" id="btn-en" onclick="setLanguage('en')">EN</button>
            </div>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span id="t-status"></span>
        </div>
        <div class="grid">
            <div class="info-box">
                <div class="info-label" id="t-accel-label"></div>
                <div class="info-val">
                    <svg class="lucide-icon accent-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                    <span>{{ accelerator }}</span>
                </div>
            </div>
            <div class="info-box">
                <div class="info-label" id="t-port-label"></div>
                <div class="info-val">http://127.0.0.1:{{ port }}</div>
            </div>
        </div>

        <div class="affinity-card">
            <div class="affinity-header">
                <div class="affinity-title">
                    <svg class="lucide-icon accent-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></svg>
                    <b id="t-affinity-title"></b>
                </div>
                <div class="affinity-badge" id="affinity-badge">
                    <div class="affinity-dot" id="affinity-dot"></div>
                    <span id="affinity-status-text"></span>
                </div>
            </div>
            <p class="affinity-desc" id="t-affinity-desc"></p>
            <div class="affinity-actions">
                <button class="action-btn primary" id="btn-install" onclick="installAffinityScript()">
                    <svg class="lucide-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                    <span id="t-btn-install"></span>
                </button>
                <button class="action-btn icon-btn" id="btn-refresh-affinity" onclick="checkAffinityStatus(true)">
                    <svg id="icon-refresh" class="lucide-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
                </button>
            </div>
            <div class="affinity-feedback" id="affinity-feedback" style="display: none;"></div>
        </div>

        <div class="instructions">
            <b id="t-instr-title"></b>
            <ol style="margin-left: 20px; margin-top: 8px;">
                <li id="t-step-req" style="margin-bottom: 6px;"></li>
                <li id="t-step-1" style="margin-bottom: 6px;"></li>
                <li id="t-step-2" style="margin-bottom: 6px;"></li>
                <li id="t-step-3"></li>
            </ol>
        </div>

        <div class="boosty-container">
            <a href="{{ boosty_url }}" target="_blank" class="boosty-btn">
                <svg class="boosty-icon" viewBox="0 0 235.6 292.2" fill="none">
                    <path fill="#ffffff" d="M44.3,164.5L76.9,51.6H127l-10.1,35c-0.1,0.2-0.2,0.4-0.3,0.6L90,179.6h24.8c-10.4,25.9-18.5,46.2-24.3,60.9 c-45.8-0.5-58.6-33.3-47.4-72.1 M90.7,240.6l60.4-86.9h-25.6l22.3-55.7c38.2,4,56.2,34.1,45.6,70.5 c-11.3,39.1-57.1,72.1-101.7,72.1C91.3,240.6,91,240.6,90.7,240.6z"/>
                </svg>
                <span id="t-boosty-btn"></span>
            </a>
        </div>

        <div class="footer">
            {{ app_name }} v{{ version }} <span id="t-footer-by"></span> <a href="{{ author_url }}" target="_blank" class="author-link">{{ author }}</a> &bull; <span id="t-footer-model"></span>
        </div>
    </div>

    <script>
        // =========================================================================
        // ВСЕ ТЕКСТЫ ИНТЕРФЕЙСА (ДЛЯ РЕДАКТИРОВАНИЯ):
        // =========================================================================
        const translations = {
            ru: {
                byPrefix: "от",
                boostyBtn: "Поддержать на Boosty",
                status: "Локальный сервер активен и готов к работе",
                accelLabel: "Аппаратный ускоритель",
                portLabel: "Порт API",
                affinityTitle: "Интеграция с Affinity",
                affinityDesc: "Установка скрипта в Affinity без сторонних менеджеров.",
                btnInstall: "Установить скрипт в Affinity",
                btnRefreshTitle: "Обновить статус подключения",
                affChecking: "Проверка...",
                affOnline: "Affinity подключен",
                affInstalled: "Affinity подключен (скрипт установлен)",
                affOffline: "Affinity не обнаружен",
                installSuccess: "Скрипт успешно установлен в панель Scripts в Affinity!",
                installAlready: "Скрипт Bubblyzer уже установлен в панели Scripts в Affinity!",
                affTip: "Убедитесь, что Affinity запущен, в настройках включен MCP (Edit → Settings → Model Context Protocol → Enable Affinity MCP; после включения перезапустите Affinity) и в панели Scripts (Window → General → Scripts) создана любая категория.",
                instrTitle: "Как подготовить и использовать:",
                stepReq: "<b>Требования в Affinity:</b> включите MCP (<code>Edit → Settings → Model Context Protocol → Enable Affinity MCP</code> — <i>после включения перезапустите Affinity!</i>) и откройте панель скриптов (<code>Window → General → Scripts</code>), создав в ней категорию, если ее нет (например, <i>My Scripts</i>).",
                step1: "Откройте проект комикса в <b>Affinity by Canva</b>.",
                step2: "Нажмите кнопку <b>«Установить скрипт в Affinity»</b> выше.",
                step3: "Запустите скрипт кликом по нему в панели <b>Scripts</b> в Affinity — нейросеть автоматически найдет пузыри и расставит текстовые фреймы!",
                footerModel: "Модель YOLOv8 ONNX (автор базы: ogkalu)"
            },
            en: {
                byPrefix: "by",
                boostyBtn: "Support on Boosty",
                status: "Local server is active and ready",
                accelLabel: "Hardware Accelerator",
                portLabel: "API Port",
                affinityTitle: "Affinity Integration",
                affinityDesc: "Direct script installation without third-party managers.",
                btnInstall: "Install script into Affinity",
                btnRefreshTitle: "Refresh connection status",
                affChecking: "Checking...",
                affOnline: "Affinity connected",
                affInstalled: "Affinity connected (script installed)",
                affOffline: "Affinity not detected",
                installSuccess: "Script successfully installed into Affinity Scripts panel!",
                installAlready: "Bubblyzer script is already installed in Affinity Scripts panel!",
                affTip: "Make sure Affinity is running, MCP is enabled in Settings (Edit → Settings → Model Context Protocol → Enable Affinity MCP; restart Affinity after enabling), and a category exists in the Scripts panel (Window → General → Scripts).",
                instrTitle: "How to setup and use:",
                stepReq: "<b>Affinity Setup:</b> enable MCP server (<code>Edit → Settings → Model Context Protocol → Enable Affinity MCP</code> — <i>restart Affinity after enabling!</i>) and open the Scripts panel (<code>Window → General → Scripts</code>), creating a category if none exists (e.g. <i>My Scripts</i>).",
                step1: "Open your comic project in <b>Affinity by Canva</b>.",
                step2: "Click <b>&laquo;Install script into Affinity&raquo;</b> above.",
                step3: "Run the script by clicking it in the <b>Scripts</b> panel in Affinity — AI will automatically detect speech bubbles and generate text frames!",
                footerModel: "YOLOv8 ONNX Model (base weights by: ogkalu)"
            }
        };

        let currentLang = 'ru';

        function setLanguage(lang) {
            currentLang = lang;
            const t = translations[lang] || translations.ru;
            document.getElementById('t-by-prefix').textContent = t.byPrefix;
            document.getElementById('t-footer-by').textContent = t.byPrefix;
            document.getElementById('t-boosty-btn').textContent = t.boostyBtn;
            document.getElementById('t-status').innerHTML = t.status;
            document.getElementById('t-accel-label').textContent = t.accelLabel;
            document.getElementById('t-port-label').textContent = t.portLabel;
            document.getElementById('t-affinity-title').textContent = t.affinityTitle;
            document.getElementById('t-affinity-desc').textContent = t.affinityDesc;
            document.getElementById('t-btn-install').textContent = t.btnInstall;
            document.getElementById('btn-refresh-affinity').setAttribute('title', t.btnRefreshTitle);
            document.getElementById('t-instr-title').textContent = t.instrTitle;
            document.getElementById('t-step-req').innerHTML = t.stepReq;
            document.getElementById('t-step-1').innerHTML = t.step1;
            document.getElementById('t-step-2').innerHTML = t.step2;
            document.getElementById('t-step-3').innerHTML = t.step3;
            document.getElementById('t-footer-model').textContent = t.footerModel;

            document.getElementById('btn-ru').classList.toggle('active', lang === 'ru');
            document.getElementById('btn-en').classList.toggle('active', lang === 'en');

            // Persist preference to server config and localStorage
            try {
                localStorage.setItem('bubblyzer_lang', lang);
                fetch('/config?save=1&lang=' + lang);
            } catch(e) {}

            checkAffinityStatus();
        }

        async function checkAffinityStatus(manual = false) {
            const dot = document.getElementById('affinity-dot');
            const text = document.getElementById('affinity-status-text');
            const refreshIcon = document.getElementById('icon-refresh');
            const t = translations[currentLang] || translations.ru;

            if (manual) {
                text.textContent = t.affChecking;
                if (refreshIcon) refreshIcon.classList.add('spin');
            }
            try {
                const res = await fetch('/affinity/status');
                const data = await res.json();
                dot.className = 'affinity-dot';
                if (data.connected) {
                    if (data.installed) {
                        dot.classList.add('installed');
                        text.textContent = t.affInstalled;
                    } else {
                        dot.classList.add('connected');
                        text.textContent = t.affOnline;
                    }
                } else {
                    text.textContent = t.affOffline;
                }
            } catch(e) {
                dot.className = 'affinity-dot';
                text.textContent = t.affOffline;
            } finally {
                if (refreshIcon) refreshIcon.classList.remove('spin');
            }
        }

        async function installAffinityScript() {
            const btn = document.getElementById('btn-install');
            const fb = document.getElementById('affinity-feedback');
            const t = translations[currentLang] || translations.ru;
            btn.disabled = true;
            fb.style.display = 'block';
            fb.className = 'affinity-feedback info';
            fb.textContent = t.affChecking;

            try {
                const res = await fetch('/affinity/install', { method: 'POST' });
                const data = await res.json();
                if (data.success) {
                    if (data.already_installed) {
                        fb.className = 'affinity-feedback info';
                        fb.textContent = t.installAlready;
                    } else {
                        fb.className = 'affinity-feedback success';
                        fb.textContent = t.installSuccess;
                    }
                    checkAffinityStatus();
                } else {
                    const isAlready = (data.error && data.error.toLowerCase().includes('already exists'));
                    if (isAlready) {
                        fb.className = 'affinity-feedback info';
                        fb.textContent = t.installAlready;
                        checkAffinityStatus();
                    } else {
                        fb.className = 'affinity-feedback error';
                        fb.innerHTML = (data.error || 'Failed') + '<br><small style="opacity:0.9">' + t.affTip + '</small>';
                    }
                }
            } catch(e) {
                const isAlready = (e.message && e.message.toLowerCase().includes('already exists'));
                if (isAlready) {
                    fb.className = 'affinity-feedback info';
                    fb.textContent = t.installAlready;
                    checkAffinityStatus();
                } else {
                    fb.className = 'affinity-feedback error';
                    fb.innerHTML = e.message + '<br><small style="opacity:0.9">' + t.affTip + '</small>';
                }
            } finally {
                btn.disabled = false;
            }
        }

        // Initialize language and check status
        const initialLang = localStorage.getItem('bubblyzer_lang') || '{{ current_lang }}' || 'ru';
        setLanguage(initialLang);
        setInterval(() => checkAffinityStatus(false), 12000);
    </script>
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
    cfg = load_config()
    current_lang = cfg.get("lang", "ru")
    return render_template_string(
        HTML_DASHBOARD,
        accelerator=accelerator,
        port=DEFAULT_PORT,
        version=__version__,
        app_name=__app_name__,
        author=__author__,
        author_url=__author_url__,
        boosty_url=__boosty_url__,
        icon_data=icon_data,
        current_lang=current_lang
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
    cfg = load_config()
    if request.method == 'POST' or request.args.get('save') == '1':
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

@app.route('/affinity/status', methods=['GET'])
def affinity_status_endpoint():
    res = check_affinity_status()
    return jsonify(res)

@app.route('/affinity/install', methods=['POST'])
def affinity_install_endpoint():
    res = install_bubblyzer_script()
    status_code = 200 if res.get("success") else 500
    return jsonify(res), status_code

@app.route('/affinity/execute', methods=['POST'])
def affinity_execute_endpoint():
    res = execute_bubblyzer_script()
    status_code = 200 if res.get("success") else 500
    return jsonify(res), status_code

def start_server(processor, port=DEFAULT_PORT):
    global processor_instance
    processor_instance = processor
    app.run(host=DEFAULT_HOST, port=port, debug=False, use_reloader=False)
