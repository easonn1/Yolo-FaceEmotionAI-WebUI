// Dashboard State
let selectedFile = null;
let selectedType = null; // "image" or "video"
let activeDevice = "cpu"; // "cpu" or "cuda"
let currentStatus = "idle";
let pollInterval = null;
let statsInterval = null;
let lastLogLength = 0;
let cachedOutputImages = [];
let cachedOutputVideos = [];

// DOM Elements
const btnCpu = document.getElementById("btn-cpu");
const btnGpu = document.getElementById("btn-gpu");
const btnRun = document.getElementById("btn-run");
const btnStop = document.getElementById("btn-stop");
const statusBadge = document.getElementById("status-badge");
const selectedFileLabel = document.getElementById("selected-file-label");
const selectedTypeLabel = document.getElementById("selected-type-label");
const runProgressBar = document.getElementById("run-progress-bar");
const progressPercentage = document.getElementById("progress-percentage");
const progressStatusText = document.getElementById("progress-status-text");
const terminalBody = document.getElementById("terminal-body");

const inputImagesList = document.getElementById("input-images-list");
const inputVideosList = document.getElementById("input-videos-list");
const outputImagesList = document.getElementById("output-images-list");
const outputVideosList = document.getElementById("output-videos-list");

const tabInput = document.getElementById("tab-input");
const tabOutput = document.getElementById("tab-output");
const previewInputContainer = document.getElementById("preview-input-container");
const previewOutputContainer = document.getElementById("preview-output-container");
const outputActionsOverlay = document.getElementById("output-actions-overlay");

const previewInputImg = document.getElementById("preview-input-image");
const previewInputVid = document.getElementById("preview-input-video");
const previewOutputImg = document.getElementById("preview-output-image");
const previewOutputVid = document.getElementById("preview-output-video");

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");

// SVG Rings
const cpuRing = document.getElementById("cpu-ring");
const ramRing = document.getElementById("ram-ring");
const gpuRing = document.getElementById("gpu-ring");
const vramRing = document.getElementById("vram-ring");

const cpuText = document.getElementById("cpu-text");
const ramText = document.getElementById("ram-text");
const gpuText = document.getElementById("gpu-text");
const vramText = document.getElementById("vram-text");
const gpuNameDisplay = document.getElementById("gpu-name-display");

// Configuration
const RING_CIRCUMFERENCE = 188.5; // 2 * pi * 30

// History buffers for resource charts (similar to Task Manager)
const chartHistory = {
    cpu: Array(40).fill(0),
    ram: Array(40).fill(0),
    gpu: Array(40).fill(0),
    vram: Array(40).fill(0)
};

// Canvas drawing utility for Task Manager style wave peaks
function drawMiniChart(canvasId, dataArray, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw background grid lines (similar to Task Manager)
    ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
    ctx.lineWidth = 0.5;
    
    // Draw 3 horizontal grid lines
    for (let y = height / 4; y < height; y += height / 4) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
    // Draw vertical grid lines
    for (let x = width / 6; x < width; x += width / 6) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
    }

    if (dataArray.length < 2) return;

    const step = width / (dataArray.length - 1);
    
    // Create gradient fill underneath
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, color.replace("1)", "0.15)")); // Add alpha
    gradient.addColorStop(1, "rgba(0, 0, 0, 0)");

    // Draw stroke line
    ctx.beginPath();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = color;
    
    ctx.moveTo(0, height - (dataArray[0] / 100) * (height - 4) - 2);
    for (let i = 1; i < dataArray.length; i++) {
        const xPos = i * step;
        const yPos = height - (dataArray[i] / 100) * (height - 4) - 2;
        ctx.lineTo(xPos, yPos);
    }
    ctx.stroke();

    // Fill area below line
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();
}

// Initialize Dashboard
document.addEventListener("DOMContentLoaded", () => {
    // 1. Device selectors
    btnCpu.addEventListener("click", () => setDevice("cpu"));
    btnGpu.addEventListener("click", () => setDevice("cuda"));
    
    // 2. Load file list & history logs
    refreshFilesList();
    refreshHistory();
    
    // 3. System stats polling
    fetchSystemStats();
    statsInterval = setInterval(fetchSystemStats, 1500);

    // 4. Drag & Drop upload
    setupDragAndDrop();

    // 5. Run & Stop trigger
    btnRun.addEventListener("click", startInference);
    btnStop.addEventListener("click", stopInference);

    // 6. Check if a job is already running on page load
    checkRunningStatus();
});

// Set Execution Environment
function setDevice(device) {
    if (currentStatus === "running") return;
    activeDevice = device;
    if (device === "cpu") {
        btnCpu.classList.add("active");
        btnGpu.classList.remove("active");
    } else {
        btnCpu.classList.remove("active");
        btnGpu.classList.add("active");
    }
    logSystem(`[SYSTEM] 运行版本环境已切换至: ${device === "cpu" ? "CPU 版本 (.venv)" : "GPU 版本 (.venv-cuda)"}`);
}

// Update Radial Progress Rings
function setRingPercent(ringElement, textElement, percent, unit = "%") {
    const offset = RING_CIRCUMFERENCE - (percent / 100) * RING_CIRCUMFERENCE;
    ringElement.style.strokeDashoffset = offset;
    textElement.textContent = `${Math.round(percent)}${unit}`;
}

// Fetch CPU/GPU/RAM Stats
async function fetchSystemStats() {
    try {
        const res = await fetch("/api/system_stats");
        if (!res.ok) return;
        const stats = await res.json();
        
        // Update rings
        setRingPercent(cpuRing, cpuText, stats.cpu_usage);
        setRingPercent(ramRing, ramText, stats.ram_usage);
        setRingPercent(gpuRing, gpuText, stats.gpu_usage);
        
        // Update CPU Name Display
        const cpuNameDisplay = document.getElementById("cpu-name-display");
        if (cpuNameDisplay) {
            cpuNameDisplay.innerHTML = `<i class="fa-solid fa-microchip"></i> CPU: ${stats.cpu_name || "检测中..."}`;
        }

        // Update VRAM (Max out percentage if we have size)
        let vramPct = 0;
        if (stats.gpu_mem_total > 0) {
            vramPct = (stats.gpu_mem_used / stats.gpu_mem_total) * 100;
            const textVal = `${Math.round(stats.gpu_mem_used)}M`;
            vramText.textContent = textVal;
            const offset = RING_CIRCUMFERENCE - (vramPct / 100) * RING_CIRCUMFERENCE;
            vramRing.style.strokeDashoffset = offset;
            gpuNameDisplay.innerHTML = `<i class="fa-solid fa-bolt"></i> GPU: ${stats.gpu_name}`;
        } else {
            vramText.textContent = "0MB";
            vramRing.style.strokeDashoffset = RING_CIRCUMFERENCE;
            gpuNameDisplay.innerHTML = `<i class="fa-solid fa-bolt"></i> GPU: 未检测到独立显卡`;
        }

        // Push new data points to chart histories
        chartHistory.cpu.push(stats.cpu_usage);
        chartHistory.cpu.shift();

        chartHistory.ram.push(stats.ram_usage);
        chartHistory.ram.shift();

        chartHistory.gpu.push(stats.gpu_usage);
        chartHistory.gpu.shift();

        chartHistory.vram.push(vramPct);
        chartHistory.vram.shift();

        // Draw mini charts (using colors defined in CSS variables)
        drawMiniChart("cpu-chart", chartHistory.cpu, "rgba(0, 240, 255, 1)");
        drawMiniChart("ram-chart", chartHistory.ram, "rgba(0, 255, 135, 1)");
        drawMiniChart("gpu-chart", chartHistory.gpu, "rgba(255, 159, 10, 1)");
        drawMiniChart("vram-chart", chartHistory.vram, "rgba(191, 90, 242, 1)");

    } catch (err) {
        // Silent fail to prevent log spamming
    }
}

// Refresh Files Tree
async function refreshFilesList() {
    try {
        const res = await fetch("/api/files");
        if (!res.ok) return;
        const data = await res.json();

        cachedOutputImages = data.outputs.images || [];
        cachedOutputVideos = data.outputs.videos || [];

        renderFileList(inputImagesList, data.inputs.images || [], "image", "assets/inputs/images/");
        renderFileList(inputVideosList, data.inputs.videos || [], "video", "assets/inputs/videos/");
        renderFileList(outputImagesList, data.outputs.images || [], "image", "assets/outputs/images/", true);
        renderFileList(outputVideosList, data.outputs.videos || [], "video", "assets/outputs/videos/", true);
    } catch (err) {
        logError("[SYSTEM] 加载文件列表失败: " + err);
    }
}

// Helper to render tree lists
function renderFileList(element, files, type, basePath, isOutput = false) {
    element.innerHTML = "";
    if (files.length === 0) {
        element.innerHTML = '<li class="empty-list">空目录</li>';
        return;
    }

    files.forEach(filename => {
        const li = document.createElement("li");
        li.className = "file-item";
        const fullPath = basePath + filename;
        
        if (selectedFile === fullPath) {
            li.classList.add("selected");
        }

        // Left text container
        const nameSpan = document.createElement("span");
        nameSpan.className = "file-name";
        nameSpan.textContent = filename;
        li.appendChild(nameSpan);

        // Click row/name to select
        li.addEventListener("click", (e) => {
            // If clicking on an action button inside the item, don't trigger selection
            if (e.target.closest(".file-action-btn")) return;

            document.querySelectorAll(".file-list li").forEach(item => item.classList.remove("selected"));
            li.classList.add("selected");
            
            selectedFile = fullPath;
            selectedType = type;
            
            selectedFileLabel.textContent = filename;
            selectedTypeLabel.textContent = type === "image" ? "图片素材" : "视频素材";
            
            if (!isOutput) {
                btnRun.disabled = false;
                switchPreviewTab("input");
                setPreviewMedia("input", fullPath, type);
            } else {
                btnRun.disabled = true;
                switchPreviewTab("output");
                setPreviewMedia("output", fullPath, type);
            }
        });

        // Right action buttons container
        const actionsDiv = document.createElement("div");
        actionsDiv.className = "file-actions";

        if (isOutput) {
            // Rename output file button
            const renameBtn = document.createElement("button");
            renameBtn.className = "file-action-btn";
            renameBtn.title = "重命名文件";
            renameBtn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i>';
            renameBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                renameFile(fullPath, filename, type);
            });
            actionsDiv.appendChild(renameBtn);
        }

        // Open file location button (available for both inputs and outputs!)
        const locBtn = document.createElement("button");
        locBtn.className = "file-action-btn";
        locBtn.title = "打开文件所在位置";
        locBtn.innerHTML = '<i class="fa-solid fa-folder-open"></i>';
        locBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            openFileLocation(fullPath);
        });
        actionsDiv.appendChild(locBtn);

        li.appendChild(actionsDiv);
        element.appendChild(li);
    });
}

// Preview Multi-Media
function setPreviewMedia(tabType, filePath, type) {
    const isInput = tabType === "input";
    const imgElement = isInput ? previewInputImg : previewOutputImg;
    const vidElement = isInput ? previewInputVid : previewOutputVid;
    const placeholder = document.querySelector(`#preview-${tabType}-container .no-preview-placeholder`);

    // Hide everything first
    imgElement.classList.add("hidden");
    vidElement.classList.add("hidden");
    imgElement.src = "";
    vidElement.src = "";
    vidElement.load();
    placeholder.classList.add("hidden");

    if (type === "image") {
        imgElement.src = "/" + filePath;
        imgElement.classList.remove("hidden");
    } else if (type === "video") {
        vidElement.src = "/" + filePath;
        vidElement.classList.remove("hidden");
        vidElement.load();
    }
    
    if (!isInput) {
        outputActionsOverlay.classList.remove("hidden");
    } else {
        outputActionsOverlay.classList.add("hidden");
    }
}

// Tab Switching
function switchPreviewTab(tab) {
    if (tab === "input") {
        tabInput.classList.add("active");
        tabOutput.classList.remove("active");
        previewInputContainer.classList.remove("hidden");
        previewOutputContainer.classList.add("hidden");
    } else {
        tabInput.classList.remove("active");
        tabOutput.classList.add("active");
        previewInputContainer.classList.add("hidden");
        previewOutputContainer.classList.remove("hidden");
    }
}

// Drag & Drop Upload
function setupDragAndDrop() {
    // Prevent default drag and drop behaviors globally for the whole window
    // to stop the browser from opening/playing files dropped outside the dropzone
    window.addEventListener("dragover", (e) => {
        e.preventDefault();
    }, false);
    window.addEventListener("drop", (e) => {
        e.preventDefault();
    }, false);

    dropZone.addEventListener("click", () => fileInput.click());
    
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            uploadFile(fileInput.files[0]);
        }
    });

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });
}

// Send Binary Post
async function uploadFile(file) {
    let targetName = file.name;
    const dotIndex = file.name.lastIndexOf('.');
    const originalExt = dotIndex !== -1 ? file.name.slice(dotIndex) : "";
    const baseName = dotIndex !== -1 ? file.name.slice(0, dotIndex) : file.name;
    
    // Prompt the user to rename the file before upload, pre-filling with the basename
    const userChoice = prompt(
        `【文件上传】您需要将此文件重命名吗？\n可在输入框中修改（文件格式后缀 ${originalExt} 将会自动保留）：`, 
        baseName
    );
    
    if (userChoice === null) {
        logSystem(`[SYSTEM] 文件上传已取消。`);
        return;
    }
    
    const cleanedChoice = userChoice.trim();
    if (cleanedChoice !== "") {
        targetName = cleanedChoice + originalExt;
    }

    logSystem(`[SYSTEM] 正在上传文件并保存为: ${targetName}...`);
    try {
        const res = await fetch(`/api/upload?filename=${encodeURIComponent(targetName)}`, {
            method: "POST",
            body: file
        });
        
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        
        logSystem(`[SYSTEM] 上传成功！文件已保存至: ${data.path}`);
        await refreshFilesList();
        
        // Auto select newly uploaded file
        selectedFile = data.path;
        selectedType = file.type.startsWith("image") ? "image" : "video";
        selectedFileLabel.textContent = targetName;
        selectedTypeLabel.textContent = selectedType === "image" ? "图片素材" : "视频素材";
        btnRun.disabled = false;
        
        switchPreviewTab("input");
        setPreviewMedia("input", data.path, selectedType);
    } catch (err) {
        logError(`[SYSTEM] 上传文件失败: ${err.message}`);
    }
}

// Send Inference Request to Backend
async function sendInferenceRequest(outputMode) {
    logSystem(`[SYSTEM] 启动检测任务: ${selectedFile} 使用 ${activeDevice.toUpperCase()} 环境 (模式: ${outputMode === "new" ? "生成新文件" : "覆盖原结果"})...`);
    clearLocalLogs();
    
    try {
        const res = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                source: selectedType,
                file: selectedFile,
                device: activeDevice,
                output_mode: outputMode
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message);

        // Update UI status
        currentStatus = "running";
        updateBadge("running", "推理运行中");
        btnRun.classList.add("hidden");
        btnStop.classList.remove("hidden");
        btnCpu.disabled = true;
        btnGpu.disabled = true;
        
        lastLogLength = 0;
        
        // Start status polling loop
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(pollRunStatus, 500);

    } catch (err) {
        logError(`[SYSTEM] 启动失败: ${err.message}`);
        updateBadge("error", "启动失败");
    }
}

// Start YOLO Inference with conflict checking
async function startInference() {
    if (!selectedFile) return;

    // Determine default expected output name
    const parts = selectedFile.split("/");
    const filename = parts[parts.length - 1];
    const dotIndex = filename.lastIndexOf(".");
    const stem = dotIndex !== -1 ? filename.slice(0, dotIndex) : filename;
    const ext = dotIndex !== -1 ? filename.slice(dotIndex) : (selectedType === "image" ? ".jpg" : ".mp4");
    const expectedOutputName = `${stem}_result${ext}`;

    // Inspect if default output file is in cached outputs lists
    let hasConflict = false;
    if (selectedType === "image") {
        hasConflict = cachedOutputImages.includes(expectedOutputName);
    } else {
        hasConflict = cachedOutputVideos.includes(expectedOutputName);
    }

    if (hasConflict) {
        const modal = document.getElementById("conflict-modal");
        const filenameSpan = document.getElementById("conflict-filename");
        filenameSpan.textContent = filename;
        modal.classList.add("active");
        
        // Modal button listeners
        const overwriteBtn = document.getElementById("btn-confirm-overwrite");
        const newBtn = document.getElementById("btn-confirm-new");
        const cancelBtn = document.getElementById("btn-confirm-cancel");

        const clearListeners = () => {
            overwriteBtn.replaceWith(overwriteBtn.cloneNode(true));
            newBtn.replaceWith(newBtn.cloneNode(true));
            cancelBtn.replaceWith(cancelBtn.cloneNode(true));
        };

        const setupConfirmButtons = () => {
            const newOverwriteBtn = document.getElementById("btn-confirm-overwrite");
            const newNewBtn = document.getElementById("btn-confirm-new");
            const newCancelBtn = document.getElementById("btn-confirm-cancel");

            newOverwriteBtn.addEventListener("click", () => {
                modal.classList.remove("active");
                clearListeners();
                sendInferenceRequest("overwrite");
            });

            newNewBtn.addEventListener("click", () => {
                modal.classList.remove("active");
                clearListeners();
                sendInferenceRequest("new");
            });

            newCancelBtn.addEventListener("click", () => {
                modal.classList.remove("active");
                clearListeners();
                logSystem("[SYSTEM] 推理任务已取消。");
            });
        };
        
        setupConfirmButtons();
    } else {
        // No conflict, launch directly
        sendInferenceRequest("overwrite");
    }
}

// Stop current runner
async function stopInference() {
    logSystem("[SYSTEM] 正在向子进程发送停止信号...");
    try {
        const res = await fetch("/api/kill", { method: "POST" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message);
        
        logSystem("[SYSTEM] 子进程已被停止。");
        finishJob("error", "已被强制停止");
    } catch (err) {
        logError(`[SYSTEM] 终止失败: ${err.message}`);
    }
}

// Check status on load
async function checkRunningStatus() {
    try {
        const res = await fetch("/api/run_status");
        if (!res.ok) return;
        const data = await res.json();
        
        if (data.status === "running") {
            currentStatus = "running";
            updateBadge("running", "推理运行中");
            btnRun.classList.add("hidden");
            btnStop.classList.remove("hidden");
            btnCpu.disabled = true;
            btnGpu.disabled = true;
            
            selectedFile = data.input_file;
            selectedType = data.input_file.includes("/images/") ? "image" : "video";
            activeDevice = data.device_type;
            
            // Set device UI toggles
            setDevice(activeDevice);
            
            selectedFileLabel.textContent = data.input_file.split("/").pop();
            selectedTypeLabel.textContent = selectedType === "image" ? "图片素材" : "视频素材";
            
            pollInterval = setInterval(pollRunStatus, 500);
        }
    } catch (e) {}
}

// Polling execution status
async function pollRunStatus() {
    try {
        const res = await fetch("/api/run_status");
        if (!res.ok) return;
        const data = await res.json();
        
        // 1. Update progress
        runProgressBar.style.width = `${data.progress}%`;
        progressPercentage.textContent = `${data.progress}%`;
        progressStatusText.textContent = `当前进度: ${data.progress}%`;

        // 2. Stream logs
        if (data.logs && data.logs.length > lastLogLength) {
            for (let i = lastLogLength; i < data.logs.length; i++) {
                appendLogLine(data.logs[i]);
            }
            lastLogLength = data.logs.length;
        }

        // 3. Handle terminal states
        if (data.status === "completed") {
            logSystem("[SYSTEM] 推理已成功结束，结果已保存！");
            finishJob("completed", "处理完成", data.output_file);
        } else if (data.status === "error") {
            logError(`[SYSTEM] 推理发生错误: ${data.error || "未知异常"}`);
            finishJob("error", "发生错误");
        }
    } catch (err) {
        logError(`[SYSTEM] 轮询状态异常: ${err}`);
    }
}

// Conclude active jobs
function finishJob(finalStatus, badgeText, outputFile = null) {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
    
    currentStatus = "idle";
    updateBadge(finalStatus, badgeText);
    
    btnRun.classList.remove("hidden");
    btnStop.classList.add("hidden");
    btnCpu.disabled = false;
    btnGpu.disabled = false;
    
    refreshFilesList();
    refreshHistory();
    
    if (outputFile) {
        // Set output preview
        switchPreviewTab("output");
        setPreviewMedia("output", outputFile, selectedType);
        
        // Push final completion info to progress bar
        runProgressBar.style.width = "100%";
        progressPercentage.textContent = "100%";
        progressStatusText.textContent = "处理已完成";
        
        // Save current active output file path to select it globally
        selectedFile = outputFile;
    } else {
        progressStatusText.textContent = "系统空闲";
        progressPercentage.textContent = "0%";
        runProgressBar.style.width = "0%";
    }
}

// Update top header status badge
function updateBadge(state, text) {
    statusBadge.className = `status-badge ${state}`;
    statusBadge.querySelector(".text").textContent = text;
}

// Log formatting helper
function logSystem(msg) {
    appendLogLine(msg, "system-msg");
}

// History logs loader
async function refreshHistory() {
    try {
        const res = await fetch("/api/history");
        if (!res.ok) return;
        const history = await res.json();
        renderHistoryList(history);
    } catch (err) {
        logError("[SYSTEM] 加载历史记录失败: " + err);
    }
}

// Renders the historical records list
function renderHistoryList(history) {
    const listElement = document.getElementById("history-list");
    if (!listElement) return;
    
    listElement.innerHTML = "";
    if (history.length === 0) {
        listElement.innerHTML = '<li class="empty-list">无历史记录</li>';
        return;
    }
    
    history.forEach(item => {
        const li = document.createElement("li");
        li.className = "history-item";
        
        const isVideo = item.source === "video";
        const iconClass = isVideo ? "fa-solid fa-film" : "fa-solid fa-image";
        const badgeClass = item.device === "cuda" ? "gpu" : "cpu";
        const badgeLabel = item.device === "cuda" ? "GPU" : "CPU";
        const statusClass = item.status === "completed" ? "completed" : "error";
        const statusLabel = item.status === "completed" ? "成功" : "失败";
        
        li.innerHTML = `
            <div class="history-item-header">
                <span class="history-item-title" title="${item.filename}">
                    <i class="${iconClass}"></i> ${item.filename}
                </span>
                <span class="history-badge ${statusClass}">${statusLabel}</span>
            </div>
            <div class="history-item-meta">
                <span>${item.timestamp}</span>
                <span class="history-badge ${badgeClass}">${badgeLabel}</span>
            </div>
            <div class="history-item-actions">
                ${item.status === "completed" ? `
                <button class="history-btn view-btn" onclick="viewHistoryItem('${item.output_file}', '${item.source}')">
                    <i class="fa-regular fa-eye"></i> 预览
                </button>
                ` : ""}
                <button class="history-btn delete-btn" onclick="deleteHistoryItem('${item.id}')">
                    <i class="fa-regular fa-trash-can"></i> 删除
                </button>
            </div>
        `;
        
        listElement.appendChild(li);
    });
}

// Preview historical output item
function viewHistoryItem(outputFile, source) {
    if (!outputFile) return;
    selectedFile = outputFile;
    selectedType = source;
    
    // Toggle selector highlights
    document.querySelectorAll(".file-list li, .history-item").forEach(item => item.classList.remove("selected"));
    
    // Update labels
    selectedFileLabel.textContent = outputFile.split("/").pop();
    selectedTypeLabel.textContent = source === "image" ? "图片素材" : "视频素材";
    btnRun.disabled = true; // Output file, cannot run again directly
    
    // Switch tabs and set preview
    switchPreviewTab("output");
    setPreviewMedia("output", outputFile, source);
    logSystem(`[SYSTEM] 已载入历史记录预览: ${outputFile}`);
}

// Delete single history log and file
async function deleteHistoryItem(id) {
    if (!confirm("确定要删除这条历史记录以及对应的生成文件吗？\n该操作将永久从硬盘删除相关文件！")) {
        return;
    }
    try {
        const res = await fetch("/api/delete_history", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id, delete_files: true })
        });
        if (!res.ok) throw new Error(await res.text());
        logSystem(`[SYSTEM] 历史记录及对应生成文件已删除。`);
        refreshFilesList();
        refreshHistory();
    } catch (e) {
        logError(`[SYSTEM] 删除失败: ${e.message}`);
    }
}

// Clear all history logs and files
async function clearAllHistory() {
    if (!confirm("警告！确定要清除所有历史记录并删除所有已生成的视频和图片文件吗？\n此操作将清空整个历史列表并释放硬盘空间！")) {
        return;
    }
    try {
        const res = await fetch("/api/delete_history", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ delete_files: true })
        });
        if (!res.ok) throw new Error(await res.text());
        logSystem(`[SYSTEM] 所有历史记录及生成文件已清空。`);
        refreshFilesList();
        refreshHistory();
    } catch (e) {
        logError(`[SYSTEM] 清除失败: ${e.message}`);
    }
}

// Bind functions to window scope for HTML inline calls
window.viewHistoryItem = viewHistoryItem;
window.deleteHistoryItem = deleteHistoryItem;
window.clearAllHistory = clearAllHistory;
window.openFolder = openFolder;
window.openFileLocation = openFileLocation;
window.renameFile = renameFile;

function logError(msg) {
    appendLogLine(msg, "error-msg");
}

function appendLogLine(text, className = "") {
    const line = document.createElement("div");
    line.className = `log-line ${className}`;
    line.textContent = text;
    terminalBody.appendChild(line);
    
    // Auto scroll to bottom
    terminalBody.scrollTop = terminalBody.scrollHeight;
}

function clearLocalLogs() {
    terminalBody.innerHTML = "";
}

// OS folder interaction triggers
async function openFolder(type) {
    try {
        const res = await fetch("/api/open_folder", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ type })
        });
        if (!res.ok) throw new Error(await res.text());
    } catch (e) {
        logError(`[SYSTEM] 无法打开文件夹: ${e.message}`);
    }
}

// Open File Location in Windows Explorer
async function openFileLocation(filePath) {
    logSystem(`[SYSTEM] 正在请求打开文件所在位置: ${filePath}...`);
    try {
        const res = await fetch("/api/open_file_location", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file: filePath })
        });
        if (!res.ok) throw new Error(await res.text());
        logSystem(`[SYSTEM] 已成功在文件资源管理器中定位并选中文件。`);
    } catch (e) {
        logError(`[SYSTEM] 无法打开文件所在位置: ${e.message}`);
    }
}

// Rename Output Files Directly
async function renameFile(filePath, oldName, type) {
    const dotIndex = oldName.lastIndexOf('.');
    const ext = dotIndex !== -1 ? oldName.slice(dotIndex) : "";
    const base = dotIndex !== -1 ? oldName.slice(0, dotIndex) : oldName;

    const newBase = prompt(`【文件重命名】请输入新的文件名（后缀 ${ext} 将自动保留）：`, base);
    if (newBase === null) return;

    const cleanBase = newBase.trim();
    if (cleanBase === "" || cleanBase === base) return;

    const newName = cleanBase + ext;
    logSystem(`[SYSTEM] 正在重命名文件: ${oldName} -> ${newName}...`);

    try {
        const res = await fetch("/api/rename_file", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file: filePath, new_name: newName })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "未知错误");

        logSystem(`[SYSTEM] 重命名成功！`);
        
        if (selectedFile === filePath) {
            selectedFile = data.new_path;
            selectedFileLabel.textContent = newName;
        }

        await refreshFilesList();
        await refreshHistory();
    } catch (e) {
        logError(`[SYSTEM] 重命名失败: ${e.message}`);
    }
}

async function openSelectedOutputFile() {
    if (!selectedFile || !selectedFile.startsWith("assets/outputs/")) {
        logError("[SYSTEM] 未选中任何有效的输出结果文件。");
        return;
    }
    try {
        const res = await fetch("/api/open_file", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file: selectedFile })
        });
        if (!res.ok) throw new Error(await res.text());
    } catch (e) {
        logError(`[SYSTEM] 无法打开文件: ${e.message}`);
    }
}
