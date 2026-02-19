# Dashboard CCTV Lalu Lintas Kota Pontianak

![Dashboard Preview](dashboard/static/assets/logo-pemkot.png)

Aplikasi web dashboard untuk monitoring CCTV lalu lintas Kota Pontianak. Dikembangkan oleh Dinas Perhubungan Kota Pontianak.

## 🚀 Fitur Utama

- **📺 Grid View** - Tampilan multi-kamera dengan layout 2x2, 3x3, 4x4
- **🗺️ Peta Interaktif** - Leaflet + OpenStreetMap dengan marker lokasi CCTV
- **🔍 Filter Kecamatan** - Filter CCTV berdasarkan 6 kecamatan di Pontianak
- **🖥️ Fullscreen Mode** - Mode layar penuh untuk fokus ke satu kamera
- **📱 Mobile Responsive** - Optimal di desktop, tablet, dan smartphone
- **🌙 Dark Theme** - Tampilan profesional dengan tema gelap
- **🔐 Admin Panel** - Django Admin untuk CRUD data CCTV

## 📋 Persyaratan Sistem

- Docker & Docker Compose
- Python 3.11+ (jika menjalankan tanpa Docker)
- MySQL 8.0+

## 🛠️ Cara Instalasi

### Menggunakan Docker (Disarankan)

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd cctv-dashboard-pontianak
   ```

2. **Salin file environment**
   ```bash
   cp .env.example .env
   ```

3. **Edit file .env sesuai kebutuhan**
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-change-in-production
   DB_PASSWORD=your-secure-password
   ```

4. **Jalankan dengan Docker Compose**
   ```bash
   docker-compose up --build
   ```

5. **Akses aplikasi**
   - Dashboard: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

### Buat Superuser untuk Admin

```bash
docker-compose exec web python manage.py createsuperuser
```

Ikuti instruksi untuk membuat username dan password.

## 📁 Struktur Proyek

```
cctv-dashboard-pontianak/
├── cctv_pontianak/          # Django project
│   ├── settings.py          # Konfigurasi
│   ├── urls.py               # URL routing
│   └── wsgi.py               # WSGI config
├── dashboard/                # Main app
│   ├── models.py             # Model CCTV, Kecamatan
│   ├── views.py              # Views
│   ├── admin.py              # Admin config
│   ├── templates/            # HTML templates
│   ├── static/               # CSS, JS, images
│   └── management/commands/  # Management commands
├── docker-compose.yml        # Docker setup
├── Dockerfile                # Container image
├── requirements.txt          # Python dependencies
└── .env.example              # Environment template
```

## 🔧 Konfigurasi

### Environment Variables

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `DEBUG` | Mode debug | `True` |
| `SECRET_KEY` | Django secret key | - |
| `ALLOWED_HOSTS` | Host yang diizinkan | `localhost,127.0.0.1` |
| `DB_NAME` | Nama database | `cctv_pontianak` |
| `DB_USER` | Username database | `dishub_admin` |
| `DB_PASSWORD` | Password database | - |
| `DB_HOST` | Host database | `db` |
| `DB_PORT` | Port database | `3306` |

## 📊 Model Database

### Kecamatan
- `id` - Primary key
- `nama` - Nama kecamatan
- `created_at` - Waktu dibuat

### CCTV
- `id` - Primary key
- `nama_lokasi` - Nama lokasi CCTV
- `kecamatan` - Foreign key ke Kecamatan
- `youtube_video_id` - ID video YouTube
- `latitude` - Koordinat latitude
- `longitude` - Koordinat longitude
- `is_active` - Status aktif/tidak aktif
- `deskripsi` - Deskripsi lokasi
- `created_at` - Waktu dibuat
- `updated_at` - Waktu diperbarui

## 🎯 Penggunaan

### Menambah Data CCTV

1. Login ke Admin Panel (http://localhost:8000/admin)
2. Klik "CCTV" di sidebar
3. Klik "Tambah CCTV"
4. Isi form:
   - Nama Lokasi
   - Pilih Kecamatan
   - YouTube Video ID (dari URL YouTube)
   - Koordinat GPS (latitude, longitude)
5. Klik "Simpan"

### Mendapatkan YouTube Video ID

Dari URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
Video ID adalah: `dQw4w9WgXcQ`

### Mendapatkan Koordinat GPS

1. Buka Google Maps
2. Klik kanan pada lokasi
3. Salin koordinat yang muncul

## ⌨️ Keyboard Shortcuts

| Shortcut | Fungsi |
|----------|--------|
| `G` | Tampilan Grid |
| `M` | Tampilan Peta |
| `ESC` | Tutup Fullscreen |

## 🚢 Deployment ke Produksi

1. **Update .env untuk produksi**
   ```env
   DEBUG=False
   SECRET_KEY=<generate-strong-secret-key>
   ALLOWED_HOSTS=cctv.pontianak.go.id
   ```

2. **Build dan jalankan**
   ```bash
   docker-compose -f docker-compose.yml up -d --build
   ```

3. **Collect static files**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

4. **Setup reverse proxy (Nginx)** untuk HTTPS

## 🔒 Keamanan

- CSRF protection aktif
- XSS protection aktif
- SQL injection protected via Django ORM
- Session cookies secure di produksi
- Gunakan HTTPS di produksi

## 📝 License

© 2024 Dinas Perhubungan Kota Pontianak

## 📞 Kontak

Dinas Perhubungan Kota Pontianak
Jl. Sultan Abdurrahman No. 1, Pontianak, Kalimantan Barat
