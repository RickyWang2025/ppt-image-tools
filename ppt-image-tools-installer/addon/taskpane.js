/**
 * PPT图片处理工具 - 任务面板JavaScript
 */

// API基础URL（根据实际部署修改）
const API_BASE_URL = 'http://localhost:8000';

// Office初始化
Office.onReady((info) => {
  if (info.host === Office.HostType.PowerPoint) {
    console.log('PPT图片处理工具已就绪');
    initTabs();
  }
});

// 初始化标签页切换
function initTabs() {
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // 切换标签样式
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      // 切换面板
      const panels = document.querySelectorAll('.panel');
      panels.forEach(p => p.classList.remove('active'));
      document.getElementById(`panel-${tab.dataset.tab}`).classList.add('active');
    });
  });
}

// 显示加载状态
function showLoading(show) {
  document.getElementById('loading').classList.toggle('active', show);
}

// 显示状态消息
function showStatus(panelId, message, type = 'info') {
  const statusEl = document.getElementById(`${panelId}-status`);
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
  statusEl.style.display = 'block';
}

// 获取选中的图片
async function getSelectedImage() {
  return new Promise((resolve, reject) => {
    Office.context.document.getSelectedDataAsync(
      Office.CoercionType.Image,
      (result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          resolve(result.value);
        } else {
          reject(new Error('请先选中一张图片'));
        }
      }
    );
  });
}

// 将base64图片插入到幻灯片
async function insertImageToSlide(base64Data, width = null, height = null) {
  return new Promise((resolve, reject) => {
    Office.context.document.setSelectedDataAsync(
      base64Data,
      {
        coercionType: Office.CoercionType.Image,
        imageWidth: width,
        imageHeight: height
      },
      (result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          resolve();
        } else {
          reject(new Error('插入图片失败'));
        }
      }
    );
  });
}

// 调用API处理图片
async function callApi(endpoint, formData) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '处理失败');
  }

  return response.json();
}

// 下载图片并转为base64
async function downloadImageAsBase64(url) {
  const response = await fetch(`${API_BASE_URL}${url}`);
  const blob = await response.blob();

  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

// ========== 放大功能 ==========
async function processUpscale() {
  const panelId = 'upscale';

  try {
    showLoading(true);
    showStatus(panelId, '正在获取选中的图片...', 'info');

    // 获取选中图片
    const imageData = await getSelectedImage();

    showStatus(panelId, '正在处理图片...', 'info');

    // 准备表单数据
    const formData = new FormData();
    formData.append('file', dataURLtoBlob(imageData), 'image.png');
    formData.append('scale', document.getElementById('upscale-scale').value);
    formData.append('model_type', document.getElementById('upscale-model').value);
    formData.append('face_enhance', document.getElementById('upscale-face').checked);

    // 调用API
    const result = await callApi('/api/upscale/', formData);

    showStatus(panelId, '正在插入处理后的图片...', 'info');

    // 下载结果并插入
    const base64Data = await downloadImageAsBase64(result.url);
    await insertImageToSlide(base64Data);

    showStatus(panelId, `处理完成！${result.original_size[0]}x${result.original_size[1]} → ${result.output_size[0]}x${result.output_size[1]}`, 'success');

  } catch (error) {
    showStatus(panelId, `错误: ${error.message}`, 'error');
  } finally {
    showLoading(false);
  }
}

// ========== 抠图功能 ==========
async function processRemoveBg() {
  const panelId = 'removebg';

  try {
    showLoading(true);
    showStatus(panelId, '正在获取选中的图片...', 'info');

    const imageData = await getSelectedImage();

    showStatus(panelId, '正在处理图片...', 'info');

    const formData = new FormData();
    formData.append('file', dataURLtoBlob(imageData), 'image.png');
    formData.append('model', document.getElementById('removebg-model').value);

    const bgcolor = document.getElementById('removebg-bgcolor').value;
    if (bgcolor) {
      formData.append('bgcolor', bgcolor);
    }

    const result = await callApi('/api/remove-bg/', formData);

    showStatus(panelId, '正在插入处理后的图片...', 'info');

    const base64Data = await downloadImageAsBase64(result.url);
    await insertImageToSlide(base64Data);

    showStatus(panelId, '抠图完成！', 'success');

  } catch (error) {
    showStatus(panelId, `错误: ${error.message}`, 'error');
  } finally {
    showLoading(false);
  }
}

// ========== 擦除功能 ==========
async function processInpaint() {
  const panelId = 'inpaint';

  try {
    showLoading(true);
    showStatus(panelId, '提示：当前版本需要手动创建遮罩。请使用画笔工具标记要擦除的区域。', 'info');

    // 注意：完整实现需要在PPT中集成画笔功能
    // 这里提供一个简化版本，用户需要提供遮罩图片

  } catch (error) {
    showStatus(panelId, `错误: ${error.message}`, 'error');
  } finally {
    showLoading(false);
  }
}

// ========== 矢量化功能 ==========
async function processVectorize() {
  const panelId = 'vectorize';

  try {
    showLoading(true);
    showStatus(panelId, '正在获取选中的图片...', 'info');

    const imageData = await getSelectedImage();

    showStatus(panelId, '正在矢量化...', 'info');

    const formData = new FormData();
    formData.append('file', dataURLtoBlob(imageData), 'image.png');

    const preset = document.getElementById('vectorize-preset').value;
    if (preset) {
      formData.append('preset', preset);
    } else {
      formData.append('color_mode', document.getElementById('vectorize-color').value);
    }

    const result = await callApi('/api/vectorize/', formData);

    showStatus(panelId, `矢量化完成！SVG大小: ${Math.round(result.svg_length / 1024)}KB`, 'success');

    // 下载SVG并提供链接
    const svgUrl = `${API_BASE_URL}${result.url}`;

    // 创建下载链接
    const statusEl = document.getElementById(`${panelId}-status`);
    statusEl.innerHTML = `矢量化完成！<br><a href="${svgUrl}" target="_blank" style="color:#0078d4">下载SVG文件</a>`;
    statusEl.className = 'status success';

  } catch (error) {
    showStatus(panelId, `错误: ${error.message}`, 'error');
  } finally {
    showLoading(false);
  }
}

// ========== 工具函数 ==========

// DataURL转Blob
function dataURLtoBlob(dataURL) {
  const arr = dataURL.split(',');
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  return new Blob([u8arr], { type: mime });
}