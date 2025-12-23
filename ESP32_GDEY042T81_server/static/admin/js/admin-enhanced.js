// 管理后台JavaScript功能 - 增强版

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有工具提示
    initTooltips();
    
    // 初始化确认对话框
    initConfirmDialogs();
    
    // 初始化表格排序
    initTableSorting();
    
    // 初始化状态更新
    initStatusUpdates();
    
    // 初始化图片上传
    initImageUpload();
    
    // 初始化主题切换
    initThemeToggle();
    
    // 初始化动画效果
    initAnimations();
});

// 初始化主题切换
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    
    // 检查本地存储的主题设置
    const savedTheme = localStorage.getItem('adminTheme') || 'default';
    applyTheme(savedTheme);
    
    // 设置切换按钮图标
    updateThemeToggleIcon(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.classList.contains('christmas-theme') ? 'christmas' : 'default';
            const newTheme = currentTheme === 'christmas' ? 'default' : 'christmas';
            
            applyTheme(newTheme);
            localStorage.setItem('adminTheme', newTheme);
            updateThemeToggleIcon(newTheme);
            
            // 添加切换动画
            document.body.style.transition = 'all 0.5s ease';
            
            // 显示主题切换提示
            const themeName = newTheme === 'christmas' ? '圣诞节主题' : '默认主题';
            showAlert(`已切换至${themeName}`, 'success');
        });
    }
}

// 应用主题
function applyTheme(theme) {
    if (theme === 'christmas') {
        document.body.classList.add('christmas-theme');
    } else {
        document.body.classList.remove('christmas-theme');
    }
}

// 更新主题切换按钮图标
function updateThemeToggleIcon(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            if (theme === 'christmas') {
                icon.className = 'fas fa-snowflake';
            } else {
                icon.className = 'fas fa-palette';
            }
        }
    }
}

// 初始化动画效果
function initAnimations() {
    // 添加滚动动画
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // 观察所有卡片
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.classList.add('animate-prep');
        observer.observe(card);
    });
}

// 初始化工具提示
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 初始化确认对话框
function initConfirmDialogs() {
    // 为所有带有data-confirm属性的按钮添加确认对话框
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// 初始化表格排序
function initTableSorting() {
    const sortableTables = document.querySelectorAll('.table-sortable');
    sortableTables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this.getAttribute('data-sort'));
            });
        });
    });
}

// 表格排序函数
function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAsc = table.getAttribute('data-sort-order') !== 'asc';
    
    rows.sort((a, b) => {
        const aValue = a.querySelector(`td[data-column="${column}"]`).textContent.trim();
        const bValue = b.querySelector(`td[data-column="${column}"]`).textContent.trim();
        
        if (isAsc) {
            return aValue.localeCompare(bValue);
        } else {
            return bValue.localeCompare(aValue);
        }
    });
    
    // 清空表格并重新添加排序后的行
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
    
    // 更新排序状态
    table.setAttribute('data-sort-order', isAsc ? 'asc' : 'desc');
    
    // 更新排序图标
    const headers = table.querySelectorAll('th[data-sort]');
    headers.forEach(header => {
        const icon = header.querySelector('.sort-icon');
        if (icon) icon.remove();
    });
    
    const currentHeader = table.querySelector(`th[data-sort="${column}"]`);
    const icon = document.createElement('i');
    icon.className = `sort-icon fas fa-sort-${isAsc ? 'up' : 'down'} ms-1`;
    currentHeader.appendChild(icon);
}

// 初始化状态更新
function initStatusUpdates() {
    // 定期更新设备状态
    const deviceStatusElements = document.querySelectorAll('.device-status');
    if (deviceStatusElements.length > 0) {
        setInterval(updateDeviceStatus, 30000); // 每30秒更新一次
    }
}

// 更新设备状态
function updateDeviceStatus() {
    const deviceStatusElements = document.querySelectorAll('.device-status[data-device-id]');
    deviceStatusElements.forEach(element => {
        const deviceId = element.getAttribute('data-device-id');
        
        fetch(`/api/devices/${deviceId}/status`)
        .then(response => response.json())
        .then(data => {
            if (data.online) {
                element.innerHTML = '<span class="badge bg-success">在线</span>';
            } else {
                element.innerHTML = '<span class="badge bg-secondary">离线</span>';
            }
        })
        .catch(error => {
            console.error('Error updating device status:', error);
        });
    });
}

// 初始化图片上传
function initImageUpload() {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('#image');
    
    if (uploadArea && fileInput) {
        // 点击上传区域触发文件选择
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
        
        // 拖拽上传
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            uploadArea.classList.add('dragover');
        }
        
        function unhighlight() {
            uploadArea.classList.remove('dragover');
        }
        
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length) {
                fileInput.files = files;
                handleFiles(files);
            }
        }
        
        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });
        
        function handleFiles(files) {
            if (files.length) {
                const file = files[0];
                
                // 验证文件类型
                if (!file.type.startsWith('image/')) {
                    showAlert('请选择图片文件', 'danger');
                    return;
                }
                
                // 验证文件大小（限制为10MB）
                if (file.size > 10 * 1024 * 1024) {
                    showAlert('图片文件大小不能超过10MB', 'danger');
                    return;
                }
                
                // 显示图片预览
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('#imagePreview');
                    const previewImg = document.querySelector('#previewImg');
                    
                    if (preview && previewImg) {
                        previewImg.src = e.target.result;
                        preview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        }
    }
}

// 显示提示消息
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.alert-container') || createAlertContainer();
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.setAttribute('role', 'alert');
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alertElement);
    
    // 自动关闭提示
    setTimeout(() => {
        alertElement.classList.remove('show');
        setTimeout(() => {
            alertElement.remove();
        }, 300);
    }, 5000);
}

// 创建提示消息容器
function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// 推送内容到设备
function pushContent(deviceId, version) {
    if (confirm('确定要推送此内容到设备吗？')) {
        const btn = event.target;
        const originalText = btn.innerHTML;
        
        // 显示加载状态
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 推送中...';
        
        fetch(`/api/devices/${deviceId}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                version: version
            })
        })
        .then(response => response.json())
        .then(data => {
            showAlert('内容推送成功', 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('内容推送失败', 'danger');
        })
        .finally(() => {
            // 恢复按钮状态
            btn.disabled = false;
            btn.innerHTML = originalText;
        });
    }
}

// 刷新设备状态
function refreshDevice(deviceId) {
    const btn = event.target;
    const originalText = btn.innerHTML;
    
    // 显示加载状态
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 刷新中...';
    
    fetch(`/api/devices/${deviceId}/status`)
    .then(response => response.json())
    .then(data => {
        if (data.online) {
            showAlert('设备在线', 'success');
        } else {
            showAlert('设备离线', 'warning');
        }
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('获取设备状态失败', 'danger');
    })
    .finally(() => {
        // 恢复按钮状态
        btn.disabled = false;
        btn.innerHTML = originalText;
    });
}

// 删除设备
function deleteDevice(deviceId) {
    if (confirm('确定要删除此设备吗？此操作不可恢复！')) {
        const btn = event.target;
        const originalText = btn.innerHTML;
        
        // 显示加载状态
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 删除中...';
        
        fetch(`/api/devices/${deviceId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                showAlert('设备删除成功', 'success');
                setTimeout(() => {
                    window.location.href = '/admin/devices';
                }, 1000);
            } else {
                throw new Error('删除失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('设备删除失败', 'danger');
        })
        .finally(() => {
            // 恢复按钮状态
            btn.disabled = false;
            btn.innerHTML = originalText;
        });
    }
}

// 删除内容
function deleteContent(deviceId, version) {
    if (confirm('确定要删除此内容吗？此操作不可恢复！')) {
        const btn = event.target;
        const originalText = btn.innerHTML;
        
        // 显示加载状态
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 删除中...';
        
        fetch(`/api/contents/${deviceId}/${version}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                showAlert('内容删除成功', 'success');
                setTimeout(() => {
                    window.location.href = `/admin/devices/${deviceId}`;
                }, 1000);
            } else {
                throw new Error('删除失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('内容删除失败', 'danger');
        })
        .finally(() => {
            // 恢复按钮状态
            btn.disabled = false;
            btn.innerHTML = originalText;
        });
    }
}

// 格式化日期时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 复制文本到剪贴板
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    showAlert('已复制到剪贴板', 'success');
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    .animate-prep {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }
    
    .animate-in {
        opacity: 1;
        transform: translateY(0);
    }
`;
document.head.appendChild(style);