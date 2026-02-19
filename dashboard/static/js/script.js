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
// Initialize on DOM Ready
// ================================
document.addEventListener('DOMContentLoaded', function () {
    initDateTime();
    initViewToggle();
    initFilters();
    initGridLayout();

    // Fetch data via API before initializing map
    fetchCCTVData().then(() => {
        initMap();
    });

    initKeyboardShortcuts();
});

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
            } else {
                gridView.classList.remove('active');
                mapView.classList.add('active');

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

        if (kecamatanId === 'all' || cardKecamatan === kecamatanId) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
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
            // Apply maxZoom to avoid zooming in too much on a single marker
            // and avoid zooming out too far if dimensions are zero
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
// Utility Functions
// ================================
let hoverTimers = {};

function handleMouseEnter(container) {
    const videoId = container.dataset.videoId;
    if (!videoId) return;

    // Clear any existing timer to avoid flickering
    if (hoverTimers[videoId]) {
        clearTimeout(hoverTimers[videoId]);
    }

    // Delay loading slightly to avoid triggers on quick sweeps
    hoverTimers[videoId] = setTimeout(() => {
        loadVideo(container);
    }, 500); // 500ms debounce
}

function handleMouseLeave(container) {
    const videoId = container.dataset.videoId;
    if (hoverTimers[videoId]) {
        clearTimeout(hoverTimers[videoId]);
        delete hoverTimers[videoId];
    }

    // Optional: Unload video to save resources when not looking
    unloadVideo(container);
}

function loadVideo(container) {
    const videoId = container.dataset.videoId;
    const title = container.dataset.title;
    const placeholder = container.querySelector('.video-placeholder');

    if (!videoId || !placeholder || placeholder.style.display === 'none') return;

    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.className = 'cctv-video';
    iframe.src = `https://www.youtube-nocookie.com/embed/${videoId}?rel=0&autoplay=1&mute=1&modestbranding=1&controls=0&showinfo=0&fs=0`;
    iframe.title = title;
    iframe.frameBorder = '0';
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    iframe.allowFullscreen = true;
    iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');

    // Remove placeholder and add iframe
    placeholder.style.display = 'none';
    container.appendChild(iframe);
}

function unloadVideo(container) {
    const iframe = container.querySelector('iframe.cctv-video');
    const placeholder = container.querySelector('.video-placeholder');

    if (iframe && placeholder) {
        iframe.remove();
        placeholder.style.display = 'flex';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ================================
// Add custom marker styles dynamically
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
        /* Remove redundant padding-top as it's already in .cctv-video-container */
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
`;
document.head.appendChild(style);
