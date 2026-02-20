/**
 * Dashboard CCTV Lalu Lintas Kota Pontianak
 * JavaScript - Interactivity & Map
 */

// ================================
// Global Variables
// ================================
let map = null;
let markers = [];
let cctvData = []; // Data will be loaded via API
let currentView = 'grid';
let currentFilter = 'all';

// ================================
// [LANGKAH 1, 2, 3, 4] - Smart Stream Manager
// ================================
const StreamManager = {
    // Konfigurasi batas concurrent streams (Langkah 2)
    maxConcurrent: 4,

    // Tracking iframe yang sedang aktif: Map<videoContainer, true>
    activeStreams: new Map(),

    // IntersectionObserver instance (Langkah 1)
    observer: null,

    // Inisialisasi observer
    init() {
        this.observer = new IntersectionObserver(
            (entries) => this._handleIntersection(entries),
            {
                root: null,         // viewport
                rootMargin: '0px',
                threshold: 0.3      // 30% terlihat = mulai load
            }
        );
    },

    // Pasang observer ke sebuah container video
    observe(container) {
        if (this.observer) {
            this.observer.observe(container);
        }
    },

    // Cabut observer dari container
    unobserve(container) {
        if (this.observer) {
            this.observer.unobserve(container);
        }
    },

    // [Langkah 1 & 3] Handler saat card masuk/keluar viewport
    _handleIntersection(entries) {
        entries.forEach(entry => {
            const container = entry.target;
            if (entry.isIntersecting) {
                // Card terlihat di layar → coba load jika slot tersedia
                this._tryLoad(container);
            } else {
                // [Langkah 3] Card keluar viewport → unload untuk hemat resource
                this._unload(container);
            }
        });
    },

    // [Langkah 2] Coba load dengan memperhatikan batas maksimum
    _tryLoad(container) {
        // Sudah diload? Skip
        if (this.activeStreams.has(container)) return;

        // Belum ada slot? Skip (tunggu sampai ada yang unload)
        if (this.activeStreams.size >= this.maxConcurrent) {
            container.dataset.pendingLoad = 'true';
            this._showWaitingBadge(container);
            return;
        }

        this._load(container);
    },

    // Load iframe YouTube ke dalam container
    _load(container) {
        const videoId = container.dataset.videoId;
        const title = container.dataset.title;
        if (!videoId) return;

        const placeholder = container.querySelector('.video-placeholder');
        if (!placeholder) return;

        // Sudah ada iframe? Jangan dobel
        if (container.querySelector('iframe.cctv-video')) return;

        const iframe = document.createElement('iframe');
        iframe.className = 'cctv-video';
        iframe.src = `https://www.youtube-nocookie.com/embed/${videoId}?rel=0&autoplay=1&mute=1&modestbranding=1&controls=0&showinfo=0&fs=0`;
        iframe.title = title || videoId;
        iframe.frameBorder = '0';
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
        iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');

        placeholder.style.display = 'none';
        container.appendChild(iframe);

        this.activeStreams.set(container, true);
        container.dataset.pendingLoad = 'false';
        this._removeBadge(container, 'waiting-badge');

        // [Langkah 4] Update indikator
        this._updateIndicator();
    },

    // [Langkah 3] Unload iframe dari container
    _unload(container) {
        const iframe = container.querySelector('iframe.cctv-video');
        const placeholder = container.querySelector('.video-placeholder');

        if (iframe) {
            iframe.remove();
        }
        if (placeholder) {
            placeholder.style.display = '';
        }

        const wasActive = this.activeStreams.has(container);
        this.activeStreams.delete(container);
        container.dataset.pendingLoad = 'false';
        this._removeBadge(container, 'waiting-badge');

        // Jika ada slot baru, coba load yang sedang pending
        if (wasActive) {
            this._promotePending();
            // [Langkah 4] Update indikator
            this._updateIndicator();
        }
    },

    // Setelah ada slot kosong, load card pending pertama yang terlihat
    _promotePending() {
        const allContainers = document.querySelectorAll('.cctv-video-container');
        for (const container of allContainers) {
            if (container.dataset.pendingLoad === 'true') {
                // Cek apakah masih di viewport
                const rect = container.getBoundingClientRect();
                const inViewport = (
                    rect.top < window.innerHeight &&
                    rect.bottom > 0 &&
                    rect.left < window.innerWidth &&
                    rect.right > 0
                );
                if (inViewport) {
                    this._load(container);
                    break;
                }
            }
        }
    },

    // Tampilkan badge "Antrian" di card yang sedang pending
    _showWaitingBadge(container) {
        if (container.querySelector('.waiting-badge')) return;
        const badge = document.createElement('div');
        badge.className = 'waiting-badge';
        badge.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            Menunggu slot...
        `;
        container.appendChild(badge);
    },

    _removeBadge(container, className) {
        const badge = container.querySelector(`.${className}`);
        if (badge) badge.remove();
    },

    // [Langkah 4] Update tampilan indikator aktif di header control bar
    _updateIndicator() {
        const indicator = document.getElementById('active-stream-indicator');
        if (!indicator) return;
        const active = this.activeStreams.size;
        const max = this.maxConcurrent;
        indicator.querySelector('.active-count').textContent = active;
        indicator.querySelector('.max-count').textContent = max;

        // Warna berubah berdasarkan tingkat penggunaan
        indicator.className = 'stream-indicator';
        if (active === max) {
            indicator.classList.add('full');
        } else if (active > 0) {
            indicator.classList.add('partial');
        }
    },

    // Ubah batas concurrent dari luar (dipanggil saat user ganti selector)
    setMaxConcurrent(n) {
        this.maxConcurrent = n;
        this._updateIndicator();
        // Jika batas dinaikkan, promote pending
        this._promotePending();
        // Jika batas diturunkan, tidak paksa unload yang sudah jalan
    },

    // Unload semua stream (dipanggil saat switch ke Map view)
    unloadAll() {
        const allContainers = document.querySelectorAll('.cctv-video-container');
        allContainers.forEach(c => this._unload(c));
    },

    // Pasang ulang observer ke semua container yang ada
    reobserveAll() {
        const allContainers = document.querySelectorAll('.cctv-video-container');
        allContainers.forEach(c => this.observe(c));
    }
};

// ================================
// Initialize on DOM Ready
// ================================
document.addEventListener('DOMContentLoaded', function () {
    initDateTime();
    initViewToggle();
    initFilters();
    initGridLayout();
    initMaxStreamSelector(); // [Langkah 2] Init selector

    // Inisialisasi StreamManager [Langkah 1]
    StreamManager.init();

    // Pasang observer ke semua card yang ada
    document.querySelectorAll('.cctv-video-container').forEach(container => {
        StreamManager.observe(container);
    });

    // Update indikator awal [Langkah 4]
    StreamManager._updateIndicator();

    // Fetch data via API before initializing map
    fetchCCTVData().then(() => {
        initMap();
    });

    initKeyboardShortcuts();
});

// ================================
// [Langkah 2] Inisialisasi selector Max Live Streams
// ================================
function initMaxStreamSelector() {
    const selector = document.getElementById('max-streams');
    if (!selector) return;

    // Set default value di selector sesuai StreamManager
    selector.value = StreamManager.maxConcurrent;

    selector.addEventListener('change', function () {
        const val = parseInt(this.value, 10);
        StreamManager.setMaxConcurrent(val);
    });
}

// ================================
// Data Fetching
// ================================
async function fetchCCTVData() {
    try {
        const response = await fetch('/api/cctv/');
        const result = await response.json();
        if (result.success) {
            cctvData = result.data;
            console.log("CCTV Data Loaded via API:", cctvData);
        } else {
            console.error("Failed to fetch CCTV data:", result.message);
        }
    } catch (error) {
        console.error("Error fetching CCTV data:", error);
    }
}

// ================================
// DateTime Display
// ================================
function initDateTime() {
    const datetimeEl = document.getElementById('datetime');
    if (!datetimeEl) return;

    function updateDateTime() {
        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
            timeZone: 'Asia/Pontianak'
        };

        datetimeEl.textContent = now.toLocaleDateString('id-ID', options);
    }

    updateDateTime();
    setInterval(updateDateTime, 1000);
}

// ================================
// View Toggle (Grid/Map)
// ================================
function initViewToggle() {
    const viewBtns = document.querySelectorAll('.view-btn');
    const gridView = document.getElementById('grid-view');
    const mapView = document.getElementById('map-view');

    viewBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const view = this.dataset.view;

            // Update buttons
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Update views
            if (view === 'grid') {
                gridView.classList.add('active');
                mapView.classList.remove('active');

                // Re-observe semua container setelah kembali ke grid
                setTimeout(() => StreamManager.reobserveAll(), 100);
            } else {
                gridView.classList.remove('active');
                mapView.classList.add('active');

                // [Langkah 3] Unload semua stream saat pindah ke map view
                StreamManager.unloadAll();

                // Invalidate map size when shown and refit bounds
                if (map) {
                    setTimeout(() => {
                        map.invalidateSize();
                        // Refit bounds once size is known
                        if (markers.length > 0) {
                            const group = new L.featureGroup(markers);
                            if (group.getBounds().isValid()) {
                                map.fitBounds(group.getBounds().pad(0.1), { maxZoom: 15 });
                            }
                        }
                    }, 200);
                }
            }

            currentView = view;
        });
    });
}

// ================================
// Filters
// ================================
function initFilters() {
    const kecamatanFilter = document.getElementById('filter-kecamatan');

    if (kecamatanFilter) {
        kecamatanFilter.addEventListener('change', function () {
            currentFilter = this.value;
            filterCCTV(currentFilter);
        });
    }
}

function filterCCTV(kecamatanId) {
    const cards = document.querySelectorAll('.cctv-card');
    let visibleCount = 0;

    cards.forEach(card => {
        const cardKecamatan = card.dataset.kecamatan;
        const container = card.querySelector('.cctv-video-container');

        if (kecamatanId === 'all' || cardKecamatan === kecamatanId) {
            card.style.display = 'block';
            visibleCount++;
            // Re-observe supaya Intersection Observer re-evaluate
            if (container) StreamManager.observe(container);
        } else {
            card.style.display = 'none';
            // Unload video yang disembunyikan
            if (container) StreamManager._unload(container);
        }
    });

    // Update total count
    const totalCCTVEl = document.getElementById('total-cctv');
    if (totalCCTVEl) {
        totalCCTVEl.textContent = visibleCount;
    }

    // Update map markers
    updateMapMarkers(kecamatanId);
}

// ================================
// Grid Layout
// ================================
function initGridLayout() {
    const layoutSelect = document.getElementById('grid-layout');
    const grid = document.getElementById('cctv-grid');

    if (layoutSelect && grid) {
        layoutSelect.addEventListener('change', function () {
            const columns = this.value;
            grid.dataset.columns = columns;

            // Setelah layout berubah, trigger re-evaluate observer
            setTimeout(() => {
                StreamManager.unloadAll();
                StreamManager.reobserveAll();
            }, 100);
        });
    }
}

// ================================
// Map Initialization
// ================================
function initMap() {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;

    // Initialize map centered on Pontianak
    map = L.map('map', {
        center: [-0.0226, 109.3425],
        zoom: 13,
        zoomControl: true
    });

    // Add tile layer (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    // Add markers for all CCTV
    addMapMarkers();
}

function addMapMarkers() {
    if (!map || cctvData.length === 0) return;

    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    // Add markers
    let addedCount = 0;
    cctvData.forEach(cctv => {
        // Skip if coordinates are truly missing (null)
        if (cctv.latitude === null || cctv.longitude === null) {
            console.warn(`Skipping CCTV ${cctv.id} due to missing coordinates`);
            return;
        }

        // Convert to float just in case they are strings
        const lat = parseFloat(cctv.latitude);
        const lng = parseFloat(cctv.longitude);

        if (isNaN(lat) || isNaN(lng)) {
            console.error(`Invalid coordinates for CCTV ${cctv.id}:`, cctv.latitude, cctv.longitude);
            return;
        }

        // Custom marker icon based on status
        const isActive = cctv.is_active;
        const statusClass = isActive ? '' : 'inactive';

        const cctvIcon = L.divIcon({
            className: 'custom-marker-container',
            html: `
                <div class="custom-marker ${statusClass}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                        <circle cx="12" cy="13" r="4"></circle>
                    </svg>
                </div>
            `,
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -16]
        });

        const marker = L.marker([lat, lng], {
            icon: cctvIcon,
            title: cctv.nama_lokasi
        });

        // Current status label
        const statusLabel = isActive ? 'Aktif' : 'Tidak Aktif';
        const statusBadgeClass = isActive ? 'active' : 'inactive';

        // Create popup content
        const popupContent = `
            <div class="popup-content">
                <div class="popup-header-row">
                    <h4 class="popup-title">${escapeHtml(cctv.nama_lokasi)}</h4>
                    <span class="cctv-status ${statusBadgeClass}">
                        <span class="status-dot"></span>
                        ${statusLabel}
                    </span>
                </div>
                <p class="popup-kecamatan">${escapeHtml(cctv.kecamatan)}</p>
                <div class="cctv-video-container popup-video-wrapper" data-video-id="${cctv.youtube_video_id}" data-title="${escapeHtml(cctv.nama_lokasi)}">
                    <div class="video-placeholder" onclick="loadVideo(this.parentElement)">
                        <img src="https://img.youtube.com/vi/${cctv.youtube_video_id}/hqdefault.jpg" alt="${escapeHtml(cctv.nama_lokasi)}" class="video-thumbnail" loading="lazy">
                        <div class="play-button small">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M8 5v14l11-7z"></path>
                            </svg>
                        </div>
                    </div>
                </div>
                <button class="popup-btn" onclick="openFullscreen(${cctv.id}, '${escapeHtml(cctv.nama_lokasi)}', '${cctv.youtube_video_id}', '${escapeHtml(cctv.kecamatan)}')">
                    Layar Penuh
                </button>
            </div>
        `;

        marker.bindPopup(popupContent, {
            maxWidth: 320,
            className: 'custom-popup'
        });

        // Store kecamatan_id for filtering
        marker.kecamatanId = cctv.kecamatan_id;

        marker.addTo(map);
        markers.push(marker);
        addedCount++;
    });

    console.log(`Added ${addedCount} markers to map`);

    // Fit bounds only if markers exist and map is likely visible
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        if (group.getBounds().isValid()) {
            map.fitBounds(group.getBounds().pad(0.1), { maxZoom: 15 });
        }
    }
}

function updateMapMarkers(kecamatanId) {
    markers.forEach(marker => {
        if (kecamatanId === 'all' || marker.kecamatanId.toString() === kecamatanId) {
            marker.addTo(map);
        } else {
            map.removeLayer(marker);
        }
    });
}

// ================================
// Fullscreen Modal
// ================================
function openFullscreen(id, title, videoId, kecamatan) {
    const modal = document.getElementById('fullscreen-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalKecamatan = document.getElementById('modal-kecamatan');
    const modalVideo = document.getElementById('modal-video');

    if (modal && modalTitle && modalVideo) {
        modalTitle.textContent = title;
        modalKecamatan.textContent = kecamatan;
        // Use youtube-nocookie and ensure params are correct for autoplay, and disable native fullscreen
        modalVideo.src = `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&mute=0&controls=1&rel=0&fs=0`;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeFullscreen() {
    const modal = document.getElementById('fullscreen-modal');
    const modalVideo = document.getElementById('modal-video');

    if (modal) {
        modal.classList.remove('active');
        modalVideo.src = '';
        document.body.style.overflow = '';
    }
}

// Close modal on backdrop click
document.addEventListener('click', function (e) {
    const modal = document.getElementById('fullscreen-modal');
    if (e.target === modal) {
        closeFullscreen();
    }
});

// ================================
// Keyboard Shortcuts
// ================================
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function (e) {
        // ESC to close modal
        if (e.key === 'Escape') {
            closeFullscreen();
        }

        // G for grid view
        if (e.key === 'g' && !e.ctrlKey && !e.metaKey) {
            const gridBtn = document.querySelector('.view-btn[data-view="grid"]');
            if (gridBtn) gridBtn.click();
        }

        // M for map view
        if (e.key === 'm' && !e.ctrlKey && !e.metaKey) {
            const mapBtn = document.querySelector('.view-btn[data-view="map"]');
            if (mapBtn) mapBtn.click();
        }
    });
}

// ================================
// Legacy: loadVideo / unloadVideo
// (masih dipakai oleh popup peta & onclick thumbnail)
// ================================
function loadVideo(container) {
    // Gunakan StreamManager untuk konsistensi slot management
    StreamManager._tryLoad(container);
}

function unloadVideo(container) {
    StreamManager._unload(container);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ================================
// Add custom marker + stream badge styles
// ================================
const style = document.createElement('style');
style.textContent = `
    .custom-marker-container {
        background: transparent;
        border: none;
    }
    .custom-marker {
        width: 32px;
        height: 32px;
        background: #3b82f6;
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .custom-marker-container:hover .custom-marker {
        transform: scale(1.15) translateY(-2px);
        background: #2563eb;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.5);
    }
    .play-button.small {
        width: 44px;
        height: 44px;
        background: rgba(59, 130, 246, 0.9);
    }
    .popup-video-wrapper {
        margin-bottom: 10px;
        border-radius: 8px;
        overflow: hidden;
    }
    .popup-video-wrapper .video-placeholder {
        display: flex;
    }
    .popup-video-wrapper .video-thumbnail {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .custom-marker.inactive {
        background: #ef4444;
    }
    .custom-marker-container:hover .custom-marker.inactive {
        background: #dc2626;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.5);
    }
    .popup-header-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 5px;
    }
    .popup-header-row .popup-title {
        margin-bottom: 0;
        flex: 1;
    }
    .popup-header-row .cctv-status {
        font-size: 11px;
        padding: 2px 6px;
    }

    /* === Waiting Badge [Langkah 3] === */
    .waiting-badge {
        position: absolute;
        top: 8px;
        left: 8px;
        background: rgba(0, 0, 0, 0.65);
        color: #facc15;
        font-size: 11px;
        font-weight: 500;
        padding: 4px 8px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
        backdrop-filter: blur(4px);
        z-index: 10;
        pointer-events: none;
    }

    /* === Stream Indicator [Langkah 4] === */
    .stream-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        font-size: 12px;
        font-weight: 600;
        color: #94a3b8;
        transition: all 0.3s ease;
    }
    .stream-indicator .indicator-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #475569;
        transition: background 0.3s;
    }
    .stream-indicator.partial .indicator-dot {
        background: #22c55e;
        box-shadow: 0 0 6px rgba(34, 197, 94, 0.6);
        animation: pulse-green 1.5s infinite;
    }
    .stream-indicator.partial {
        color: #22c55e;
        border-color: rgba(34, 197, 94, 0.3);
    }
    .stream-indicator.full .indicator-dot {
        background: #f59e0b;
        box-shadow: 0 0 6px rgba(245, 158, 11, 0.6);
        animation: pulse-amber 1.5s infinite;
    }
    .stream-indicator.full {
        color: #f59e0b;
        border-color: rgba(245, 158, 11, 0.3);
    }
    @keyframes pulse-green {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.3); }
    }
    @keyframes pulse-amber {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.3); }
    }
`;
document.head.appendChild(style);
