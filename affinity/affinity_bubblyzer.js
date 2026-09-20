/**
 * name: Bubblyzer by BATCOM
 * description: Comic speech bubble detector powered by ONNX AI and Affinity integration.
 * version: 1.2.0
 */

const docModule = require('/document');
const AffinityDocument = docModule.Document;
const FileExportOptions = docModule.FileExportOptions;
const FileExportArea = docModule.FileExportArea;

let ErrorCode = null;
try {
    ErrorCode = require('affinity:common').ErrorCode;
} catch (e) {}

function isPermissionDenied(err) {
    if (!err) return false;
    if (ErrorCode && err.errorCode === ErrorCode.PERMISSION_DENIED) return true;
    let msg = String(err.message || err);
    return msg.indexOf("PERMISSION_DENIED") !== -1 || msg.indexOf("Permission denied") !== -1;
}

function getCandidateTempPaths(doc) {
    let paths = [];
    if (typeof app !== 'undefined' && app.userDesktopPath) {
        let base = app.userDesktopPath.replace(/[/\\]+$/, '');
        paths.push(base + "/Bubblyzer_temp_export.png");
    }
    try {
        if (doc && doc.path) {
            let docDir = doc.path.replace(/[/\\][^/\\]*$/, '');
            if (docDir && !paths.some(p => p.startsWith(docDir))) {
                paths.push(docDir + "/Bubblyzer_temp_export.png");
            }
        }
    } catch (e) {}
    paths.push("Bubblyzer_temp_export.png");
    return paths;
}

function isDialogOk(result) {
    if (result === null || result === undefined) return false;
    if (result === 0 || result === 1) return true;
    if (result == 0) return true;
    if (typeof DialogResult !== 'undefined' && DialogResult) {
        if (result === DialogResult.Ok || result === DialogResult.OK) return true;
        if (result == DialogResult.Ok) return true;
        if (DialogResult.Ok && typeof result.equals === 'function' && result.equals(DialogResult.Ok)) return true;
        if (typeof result.value !== 'undefined' && DialogResult.Ok && (result.value === DialogResult.Ok.value || result.value === 0)) return true;
    }
    if (typeof result.value !== 'undefined' && (result.value === 0 || result.value === 1)) return true;
    let str = String(result).toLowerCase();
    return str.indexOf("ok") !== -1 || str === "0";
}

const { StoryBuilder } = require('/storybuilder');
const { FrameTextNodeDefinition, ContainerNodeDefinition } = require('/nodes');
const { Rectangle } = require('/geometry');
const { DocumentCommand, AddChildNodesCommandBuilder } = require('/commands');
const { Dialog, DialogResult, UnitType } = require('/dialog');
const { app } = require('/application');

// Базовый адрес локального сервера Bubblyzer
const SERVER_PORT = 28734;
const SERVER_URL = "http://127.0.0.1:" + SERVER_PORT;

// Модуль файловой системы для очистки временных файлов
let fsModule = null;
try {
    fsModule = require('/fs');
} catch (e) {}

async function removeFileSafe(filePath) {
    if (!filePath || !fsModule) return;
    try {
        if (fsModule.promises && fsModule.promises.remove) {
            await fsModule.promises.remove(filePath);
        } else if (fsModule.FileSystemApi && fsModule.FileSystemApi.removeAsync) {
            fsModule.FileSystemApi.removeAsync(filePath, () => {});
        }
    } catch (e) {}
}

// Пытаемся импортировать HttpRequest, если он в модуле
let HttpReq = null;
try {
    let net = require('/network') || require('/http');
    if (net && net.HttpRequest) HttpReq = net.HttpRequest;
    else if (net && net.HttpRequestApi) HttpReq = net.HttpRequestApi;
} catch (e) {}

if (!HttpReq) {
    if (typeof HttpRequest !== 'undefined') HttpReq = HttpRequest;
    else if (typeof HttpRequestApi !== 'undefined') HttpReq = HttpRequestApi;
}

// Локализация интерфейса (Русский и English)
const I18N = {
    ru: {
        dialogTitle: "Bubblyzer от BATCOM",
        langGroupTitle: "Language",
        langLabel: "Change language and click OK to immediately reload this dialog.",
        langOptions: ["Русский (RU)", "English (EN)"],
        warningTitle: "⚠  Внимание",
        warningText: "Нейросеть ищет пузыри только с текстом. Не стирайте текст перед сканированием.",
        paramsTitle: "👁️ Параметры сканирования",
        scopeLabel: "",
        scopeOptions: [
            "Текущая страница",
            "Весь документ",
            "Выборочные страницы (например, 1-3, 5)"
        ],
        pagesLabel: "",
        confLabel: "Порог уверенности (меньше = внимательнее):",
        groupSwitchLabel: "Группировать фреймы в слой?",
        layerName: "Bubbles",
        noDoc: "Нет активного документа в Affinity.",
        noPages: "Не выбрано ни одной страницы для обработки.",
        exportFailed: "Не удалось экспортировать страницу.",
        permissionFsError: "Affinity заблокировал экспорт страницы (PERMISSION_DENIED).\n\nВ обновлении Affinity скриптам требуются явные разрешения безопасности:\n\n1. Откройте в меню: Edit → Settings → Scripting (Правка → Настройки → Скриптинг).\n2. Включите галочки 'Access the file system' и 'Access networks'.\n3. В блоке 'File System access' нажмите '+' и добавьте папку Рабочего стола (Desktop) или папку с проектом.\n4. В панели Scripts Library нажмите правой кнопкой мыши на 'Bubblyzer by BATCOM' → выберите 'Mark as Trusted'.",
        permissionNetError: "Affinity заблокировал сетевое соединение (PERMISSION_DENIED).\n\nСкрипту требуется доступ к локальной сети для связи с сервером Bubblyzer:\n\n1. Откройте: Edit → Settings → Scripting (Правка → Настройки → Скриптинг).\n2. Включите галочку 'Access networks' (Доступ к сети).\n3. В панели Scripts Library нажмите правой кнопкой на скрипт → 'Mark as Trusted'.",
        noHttp: "В вашей версии Affinity не найден модуль HttpRequest / Network API.",
        connectError: (url, err) => `Не удалось подключиться к серверу Bubblyzer (${url}).\n\nОшибка: ${err}\n\nПожалуйста, проверьте, что локальный сервер Bubblyzer запущен!`,
        emptyResponse: "Сервер Bubblyzer вернул пустой ответ.",
        serverError: (err) => `Ошибка сервера Bubblyzer: ${err}`,
        invalidFormat: "Сервер вернул неожиданный формат данных.",
        jsonError: (err) => `Не удалось распарсить JSON-ответ сервера: ${err}`,
        successAlert: (pages, total, bubbles) => `Готово!\n\nУспешно обработано страниц: ${pages} из ${total}\nСоздано текстовых фреймов: ${bubbles}`,
        failAlert: "Не удалось обработать выбранные страницы.",
        alertTitleSuccess: "Bubblyzer от BATCOM",
        alertTitleError: "Bubblyzer — Ошибка",
        alertTitleWarning: "Bubblyzer — Предупреждение"
    },
    en: {
        dialogTitle: "Bubblyzer by BATCOM",
        langGroupTitle: "Язык интерфейса",
        langLabel: "При смене языка нажмите OK — окно мгновенно откроется на новом языке.",
        langOptions: ["Русский (RU)", "English (EN)"],
        warningTitle: "⚠  Important",
        warningText: "The AI detects speech bubbles containing text. Do not erase text before scanning.",
        paramsTitle: "👁️ Detection Settings",
        scopeLabel: "",
        scopeOptions: [
            "Current Spread",
            "All Spreads in Document",
            "Selected Spreads (e.g. 1-3, 5)"
        ],
        pagesLabel: "",
        confLabel: "Confidence Threshold (lower = more sensitive):",
        groupSwitchLabel: "Group created frames into a layer?",
        layerName: "Bubbles",
        noDoc: "No active document in Affinity.",
        noPages: "No valid pages selected for scanning.",
        exportFailed: "Failed to export spread.",
        permissionFsError: "Affinity blocked file export (PERMISSION_DENIED).\n\nThe new Affinity update requires explicit script permissions:\n\n1. Go to: Edit → Settings → Scripting.\n2. Enable 'Access the file system' and 'Access networks'.\n3. Under 'File System access', click '+' and add Desktop (or your comic folder).\n4. In Scripts Library panel, right-click 'Bubblyzer by BATCOM' → select 'Mark as Trusted'.",
        permissionNetError: "Affinity blocked network connection (PERMISSION_DENIED).\n\nThe script requires local network access to communicate with Bubblyzer:\n\n1. Go to: Edit → Settings → Scripting.\n2. Enable 'Access networks'.\n3. In Scripts Library panel, right-click 'Bubblyzer by BATCOM' → select 'Mark as Trusted'.",
        noHttp: "HttpRequest / Network API module was not found in your Affinity version.",
        connectError: (url, err) => `Could not connect to Bubblyzer server (${url}).\n\nError: ${err}\n\nPlease make sure the Bubblyzer app is running!`,
        emptyResponse: "Bubblyzer server returned an empty response.",
        serverError: (err) => `Bubblyzer server error: ${err}`,
        invalidFormat: "Server returned unexpected data format.",
        jsonError: (err) => `Failed to parse JSON response: ${err}`,
        successAlert: (pages, total, bubbles) => `Done!\n\nSuccessfully processed spreads: ${pages} of ${total}\nCreated text frames: ${bubbles}`,
        failAlert: "Failed to process selected spreads.",
        alertTitleSuccess: "Bubblyzer by BATCOM",
        alertTitleError: "Bubblyzer — Error",
        alertTitleWarning: "Bubblyzer — Warning"
    }
};

function parsePageRanges(text, maxPages) {
    let indices = new Set();
    let parts = text.split(',');
    for (let part of parts) {
        let range = part.trim().split('-');
        if (range.length === 1) {
            let p = parseInt(range[0]);
            if (!isNaN(p) && p >= 1 && p <= maxPages) indices.add(p - 1);
        } else if (range.length === 2) {
            let start = parseInt(range[0]);
            let end = parseInt(range[1]);
            if (!isNaN(start) && !isNaN(end)) {
                for (let i = start; i <= end; i++) {
                    if (i >= 1 && i <= maxPages) indices.add(i - 1);
                }
            }
        }
    }
    return Array.from(indices).sort((a,b)=>a-b);
}

// Текущие сохраненные настройки
let savedSettings = {
    mode: 0,
    pages: "",
    confidence: 40,
    groupFrames: true,
    lang: "ru"
};

function fetchSavedConfig() {
    if (!HttpReq) return;
    try {
        let req = HttpReq.create(`${SERVER_URL}/config`, "GET");
        let res = req.do();
        if (res && res.response) {
            let body = res.response.content;
            if (typeof body === 'function') body = body();
            if (body) {
                let parsed = JSON.parse(body);
                if (parsed.confidence !== undefined) savedSettings.confidence = Number(parsed.confidence);
                if (parsed.group_frames !== undefined) savedSettings.groupFrames = Boolean(parsed.group_frames);
                if (parsed.mode !== undefined) savedSettings.mode = Number(parsed.mode);
                if (parsed.pages !== undefined) savedSettings.pages = String(parsed.pages);
                if (parsed.lang !== undefined) savedSettings.lang = String(parsed.lang).toLowerCase() === "en" ? "en" : "ru";
            }
        }
    } catch (e) {}
}

function persistConfig(cfg) {
    if (!HttpReq) return;
    try {
        let url = `${SERVER_URL}/config?save=1` +
            `&confidence=${encodeURIComponent(cfg.confidence)}` +
            `&group_frames=${encodeURIComponent(cfg.groupFrames ? "true" : "false")}` +
            `&mode=${encodeURIComponent(cfg.mode)}` +
            `&pages=${encodeURIComponent(cfg.pages || "")}` +
            `&lang=${encodeURIComponent(cfg.lang || "ru")}`;
        let req = HttpReq.create(url, "GET");
        req.do();
    } catch (e) {}
}

// Вспомогательная функция для проверки успешности экспорта вне основного цикла
function checkExportSuccess(records) {
    let success = false;
    records.enumerate((record) => {
        if (record.isSuccess) success = true;
    });
    return success;
}

async function processSpreads() {
    let doc = AffinityDocument.current;
    
    // Синхронизируем настройки с сервером
    fetchSavedConfig();

    let currentLang = (savedSettings.lang === "en") ? "en" : "ru";
    let t = I18N[currentLang];

    if (!doc) {
        console.error(t.noDoc);
        if (typeof app !== 'undefined' && app.alert) {
            app.alert(t.noDoc, t.alertTitleWarning);
        }
        return;
    }

    let userCompletedDialog = false;
    let minConfidence = 0.40;
    let useLayerGroup = true;
    let spreadsToScan = [];

    // Цикл диалога: при смене языка в окне и нажатии OK окно автоматически в фоне перезагружается на новом языке
    while (!userCompletedDialog) {
        currentLang = (savedSettings.lang === "en") ? "en" : "ru";
        t = I18N[currentLang];

        let dialog = Dialog.create(t.dialogTitle);
        dialog.initialWidth = 470;

        let col = dialog.addColumn();

        // 1. БЛОК ВЫБОРА ЯЗЫКА (ComboBox для компактности)
        let langGroup = col.addGroup("🌐  " + t.langGroupTitle);
        langGroup.enableSeparator = true;

        let initialLangIndex = (currentLang === "en") ? 1 : 0;
        let langRadio = langGroup.addComboBox(t.langLabel, t.langOptions, initialLangIndex);
        langRadio.isFullWidth = true;

        // 2. БЛОК ПАРАМЕТРОВ СКАНА (включает предупреждение)
        let group = col.addGroup(t.paramsTitle);
        group.enableSeparator = true;

        let desc = group.addStaticText("", t.warningTitle + "  " + t.warningText);
        desc.isFullWidth = true;

        let initialMode = (savedSettings.mode >= 0 && savedSettings.mode <= 2) ? savedSettings.mode : 0;
        let radio = group.addRadioGroup(t.scopeLabel, t.scopeOptions, initialMode);
        radio.isFullWidth = true;

        let pagesText = group.addTextBox(t.pagesLabel, savedSettings.pages || "");
        pagesText.isFullWidth = true;
        pagesText.isEnabled = (initialMode === 2);

        let initialConf = (savedSettings.confidence >= 1 && savedSettings.confidence <= 100) ? savedSettings.confidence : 40;
        let confEditor = group.addUnitValueEditor(
            t.confLabel,
            UnitType.Number, UnitType.Number,
            initialConf, 1, 100
        )
            .setShowPopupSlider(true)
            .setPrecision(0);

        let groupSwitch = group.addSwitch(t.groupSwitchLabel, savedSettings.groupFrames !== false);

        radio.onValueChangedHandler = function() {
            pagesText.isEnabled = (radio.selectedIndex === 2);
        };
        
        let result = dialog.runModal();
        let isOk = isDialogOk(result);
        console.log(`Dialog completed with result: ${result}, isOk: ${isOk}`);
        
        if (!isOk) {
            console.log("Canceled. Result code was: " + result);
            return;
        }

        function extractVal(prop, defaultVal) {
            if (prop === null || prop === undefined) return defaultVal;
            if (typeof prop === 'number' || typeof prop === 'boolean' || typeof prop === 'string') return prop;
            if (typeof prop.value !== 'undefined') return prop.value;
            return defaultVal;
        }

        // Сохраняем текущие значения
        let langIdx = extractVal(langRadio.selectedIndex, 0);
        let selectedLang = (langIdx === 1) ? "en" : "ru";
        savedSettings.mode = extractVal(radio.selectedIndex, 0);
        savedSettings.pages = pagesText.text || "";
        let rawConf = extractVal(confEditor.value, 40);
        savedSettings.confidence = Math.round(Number(rawConf) || 40);
        savedSettings.groupFrames = Boolean(extractVal(groupSwitch.value, true));
        savedSettings.lang = selectedLang;
        persistConfig(savedSettings);

        // Если пользователь сменил язык в окне и нажал OK — бесшовно перезагружаем окно на новом языке!
        if (selectedLang !== currentLang) {
            continue;
        }

        // Пользователь нажал OK на нужном языке — переходим к сканированию
        userCompletedDialog = true;
        t = I18N[selectedLang];

        let mode = savedSettings.mode; // 0 = Current, 1 = All, 2 = Specific
        let spreadsList = [];
        try {
            if (doc.spreads && typeof doc.spreads.toArray === 'function') {
                spreadsList = doc.spreads.toArray();
            } else if (doc.spreads) {
                spreadsList = Array.from(doc.spreads);
            }
        } catch (e) {
            console.log("Could not convert spreads to array:", e.message || e);
        }

        spreadsToScan = [];
        if (mode === 0) {
            if (doc.currentSpread) {
                spreadsToScan.push(doc.currentSpread);
            } else if (spreadsList.length > 0) {
                spreadsToScan.push(spreadsList[0]);
            }
        } else if (mode === 1) {
            spreadsToScan = spreadsList;
        } else if (mode === 2) {
            let indices = parsePageRanges(pagesText.text, spreadsList.length);
            for (let i of indices) {
                spreadsToScan.push(spreadsList[i]);
            }
        }
        
        console.log(`Document spreads total: ${spreadsList.length}, spreads to scan: ${spreadsToScan.length}`);

        if (spreadsToScan.length === 0) {
            console.log(t.noPages);
            if (typeof app !== 'undefined' && app.alert) {
                app.alert(t.noPages, t.alertTitleWarning);
            }
            return;
        }
        
        minConfidence = savedSettings.confidence / 100.0;
        if (isNaN(minConfidence) || minConfidence < 0) minConfidence = 0.0;
        if (minConfidence > 1.0) minConfidence = 1.0;

        useLayerGroup = savedSettings.groupFrames;
    }

    let tempFilesToClean = new Set();
    let successPagesCount = 0;
    let totalBubblesCount = 0;
    let fatalError = null;

    console.log(`Starting Bubblyzer detection for ${spreadsToScan.length} pages (min confidence: ${Math.round(minConfidence * 100)}%)...`);

    try {
        for (let i = 0; i < spreadsToScan.length; i++) {
            let spread = spreadsToScan[i];
            console.log(`\n--- Processing page ${i+1} of ${spreadsToScan.length} ---`);
            
            // Делаем страницу текущей
            try {
                doc.executeCommand(DocumentCommand.createSetCurrentSpread(spread));
            } catch(e) {
                console.log("Could not set current spread, trying without...", e.message);
            }
            
            let exportOptions = FileExportOptions.createWithPresetName("PNG");
            let exportArea = FileExportArea.createForCurrentSpread();
            
            let usedTempPath = null;
            let exportSucceeded = false;
            let lastExportError = null;
            let candidatePaths = getCandidateTempPaths(doc);

            for (let candidate of candidatePaths) {
                try {
                    console.log(`Exporting page to ${candidate}...`);
                    let records = doc.export(candidate, exportOptions, exportArea, null);
                    if (checkExportSuccess(records)) {
                        exportSucceeded = true;
                        usedTempPath = candidate;
                        tempFilesToClean.add(candidate);
                        break;
                    }
                } catch (err) {
                    lastExportError = err;
                    console.error(`Export failed for ${candidate}: ${err.message || err}`);
                    if (!isPermissionDenied(err)) {
                        break;
                    }
                }
            }

            if (!exportSucceeded) {
                if (isPermissionDenied(lastExportError)) {
                    fatalError = t.permissionFsError;
                } else {
                    fatalError = t.exportFailed + (lastExportError ? ` (${lastExportError.message || lastExportError})` : "");
                }
                console.error(fatalError);
                break;
            }
            
            if (!HttpReq) {
                fatalError = t.noHttp;
                console.error(fatalError);
                break;
            }

            let responseStr = null;
            try {
                let url = `${SERVER_URL}/detect?image_path=` + encodeURIComponent(usedTempPath) + "&cleanup=true";
                let request = HttpReq.create(url, "GET");
                let reqResult = request.do();
                
                if (reqResult && reqResult.response) {
                    let status = reqResult.response.statusCode;
                    let statusCodeNum = (status && typeof status.value !== 'undefined') ? status.value : parseInt(status);
                    if (!isNaN(statusCodeNum) && statusCodeNum >= 400) {
                        throw new Error("HTTP " + statusCodeNum);
                    }
                    let responseObj = reqResult.response;
                    if (typeof responseObj === 'string') {
                        responseStr = responseObj;
                    } else if (responseObj && responseObj.content !== undefined) {
                        responseStr = (typeof responseObj.content === 'function') ? responseObj.content() : responseObj.content;
                    }
                } else if (typeof reqResult === 'string') {
                    responseStr = reqResult;
                }
            } catch (e) {
                if (isPermissionDenied(e)) {
                    fatalError = t.permissionNetError;
                } else {
                    fatalError = t.connectError(SERVER_URL, e.message || e);
                }
                console.error(fatalError);
                break;
            }

            if (!responseStr) {
                fatalError = t.emptyResponse;
                console.error(fatalError);
                break;
            }

            let data;
            try {
                data = JSON.parse(responseStr);
                if (data && data.error) {
                    fatalError = t.serverError(data.error);
                    console.error(fatalError);
                    break;
                }
                if (!Array.isArray(data)) {
                    fatalError = t.invalidFormat;
                    console.error(fatalError);
                    break;
                }
            } catch (e) {
                fatalError = t.jsonError(e.message);
                console.error(fatalError);
                break;
            }

            let filtered = data.filter(item => (item.confidence === undefined || item.confidence >= minConfidence));
            console.log(`Detected ${data.length} bubbles (filtered to ${filtered.length} with >= ${Math.round(minConfidence * 100)}% confidence).`);
            
            let targetParent = null;
            if (useLayerGroup && filtered.length > 0) {
                try {
                    let containerDef = ContainerNodeDefinition.create(t.layerName);
                    let builder = AddChildNodesCommandBuilder.create();
                    builder.setInsertionTarget(spread);
                    builder.addNode(containerDef);
                    let cmd = builder.createCommand(true);
                    doc.executeCommand(cmd);
                    
                    if (cmd.newNodes && cmd.newNodes.length > 0) {
                        targetParent = cmd.newNodes[0];
                    } else {
                        targetParent = spread.children.last;
                    }
                } catch(e) {
                    console.log("Could not create layer, placing directly on spread:", e.message);
                    targetParent = null;
                }
            }

            for (let item of filtered) {
                let bbox = item.bbox; 
                let x = bbox[0];
                let y = bbox[1];
                let width = bbox[2] - bbox[0];
                let height = bbox[3] - bbox[1];
                
                try {
                    let rect = new Rectangle(x, y, width, height);
                    let sb = StoryBuilder.create();
                    sb.addText(item.class);
                    let frameDef = FrameTextNodeDefinition.createFromStoryBuilder(rect, sb);
                    doc.addNode(frameDef, targetParent || spread);
                } catch (err) {
                    console.error(`Error placing text frame: ${err.message}`);
                }
            }

            successPagesCount++;
            totalBubblesCount += filtered.length;
        }
    } finally {
        // Автоматически удаляем временные файлы после завершения сканирования
        for (let filePath of tempFilesToClean) {
            await removeFileSafe(filePath);
        }
    }

    if (fatalError) {
        if (typeof app !== 'undefined' && app.alert) {
            app.alert(fatalError, t.alertTitleError);
        }
    } else if (successPagesCount > 0) {
        console.log("\nFinished processing all selected pages!");
        if (typeof app !== 'undefined' && app.alert) {
            app.alert(
                t.successAlert(successPagesCount, spreadsToScan.length, totalBubblesCount),
                t.alertTitleSuccess
            );
        }
    } else {
        if (typeof app !== 'undefined' && app.alert) {
            app.alert(t.failAlert, t.alertTitleWarning);
        }
    }
}

processSpreads().catch(err => {
    console.error("Unhandled error in Bubblyzer script:", err.message || err);
    if (typeof app !== 'undefined' && app.alert) {
        let msg = isPermissionDenied(err) ? I18N.ru.permissionFsError : ("Ошибка выполнения Bubblyzer:\n\n" + (err.stack || err.message || err));
        app.alert(msg, "Bubblyzer — Ошибка");
    }
});
