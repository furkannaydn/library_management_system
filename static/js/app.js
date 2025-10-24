// Kütüphane Yönetim Sistemi - Genel JavaScript Fonksiyonları
// Tüm sayfalarda kullanılan ortak JavaScript kodları
// Bootstrap bileşenleri, yardımcı fonksiyonlar ve API çağrıları

document.addEventListener('DOMContentLoaded', function() {
    // Sayfa yüklendiğinde çalışacak genel kodlar
    initializeApp();
    initializeTheme();
});

function initializeApp() {
    // Bootstrap tooltip'leri etkinleştir - Hover ipuçları
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Bootstrap popover'ları etkinleştir - Tıklama ipuçları
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Genel yardımcı fonksiyonlar - Tarih formatlama ve bildirimler
function formatDate(dateString) {
    // Tarih string'ini Türkçe format'a çevir - Sadece tarih
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showAlert(message, type = 'info', duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.body.appendChild(alertDiv);
    
    // Belirtilen süre sonra otomatik kapat
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, duration);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle',
        'primary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function showLoading(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    if (element) {
        element.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Yükleniyor...</span>
                </div>
            </div>
        `;
    }
}

function hideLoading(element, content = '') {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    if (element) {
        element.innerHTML = content;
    }
}

// Form validasyonu
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// API çağrıları için yardımcı fonksiyonlar
async function apiCall(url, method = 'GET', data = null) {
    try {
        const config = {
            method: method,
            url: url,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            config.data = data;
        }
        
        const response = await axios(config);
        return response.data;
    } catch (error) {
        console.error('API çağrısında hata:', error);
        throw error;
    }
}

// Sayfa yükleme animasyonu
function addPageLoadAnimation() {
    const elements = document.querySelectorAll('.card, .table, .jumbotron');
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Sayfa yüklendiğinde animasyonu başlat
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(addPageLoadAnimation, 100);
});

// Klavye kısayolları
document.addEventListener('keydown', function(e) {
    // Ctrl + N ile yeni ekleme
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        const addButton = document.querySelector('[data-bs-toggle="modal"]');
        if (addButton) {
            addButton.click();
        }
    }
    
    // Escape ile modal kapatma
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Responsive tablo için horizontal scroll
function makeTableResponsive() {
    const tables = document.querySelectorAll('.table-responsive table');
    tables.forEach(table => {
        if (table.offsetWidth > table.parentElement.offsetWidth) {
            table.parentElement.style.overflowX = 'auto';
        }
    });
}

// Sayfa yüklendiğinde responsive tabloları kontrol et
document.addEventListener('DOMContentLoaded', function() {
    makeTableResponsive();
    window.addEventListener('resize', makeTableResponsive);
});

// Otomatik kaydetme özelliği (draft)
function enableAutoSave(formId, interval = 30000) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea, select');
    const storageKey = `draft_${formId}`;
    
    // Kaydedilmiş draft'ı yükle
    const savedData = localStorage.getItem(storageKey);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        } catch (e) {
            console.warn('Draft verisi yüklenemedi:', e);
        }
    }
    
    // Otomatik kaydetme
    setInterval(() => {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        localStorage.setItem(storageKey, JSON.stringify(data));
    }, interval);
    
    // Form gönderildiğinde draft'ı temizle
    form.addEventListener('submit', () => {
        localStorage.removeItem(storageKey);
    });
}

// Gelişmiş arama fonksiyonu
function enableAdvancedSearch(tableId, searchFields = []) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Arama yapın...';
    
    table.parentElement.insertBefore(searchInput, table);
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

// Tema Yönetimi - Dark/Light mode kontrolü
function initializeTheme() {
    // Kaydedilmiş tema tercihini yükle
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function setTheme(theme) {
    const body = document.body;
    
    // Animasyon başlat
    animateThemeTransition();
    
    // Tema sınıfını güncelle
    body.setAttribute('data-theme', theme);
    
    // LocalStorage'a kaydet
    localStorage.setItem('theme', theme);
    
    // Dropdown'da aktif seçeneği işaretle
    updateThemeDropdown(theme);
}

function updateThemeDropdown(theme) {
    const dropdownItems = document.querySelectorAll('#themeDropdown + .dropdown-menu .dropdown-item');
    dropdownItems.forEach(item => {
        item.classList.remove('active');
        if (item.onclick && item.onclick.toString().includes(`'${theme}'`)) {
            item.classList.add('active');
        }
    });
}

function showThemeNotification(theme) {
    const themeNames = {
        'light': 'Açık Tema',
        'dark': 'Karanlık Tema',
        'auto': 'Otomatik Tema'
    };
    
    showAlert(`${themeNames[theme]} aktif edildi!`, 'success', 2000);
}

// Tema değişikliği animasyonu
function animateThemeTransition() {
    document.body.style.transition = 'all 0.3s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
}
