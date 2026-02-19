"""
Models untuk Dashboard CCTV Lalu Lintas Kota Pontianak
"""

from django.db import models


class Kecamatan(models.Model):
    """Model untuk menyimpan data kecamatan di Kota Pontianak"""
    
    nama = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nama Kecamatan'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Dibuat Pada'
    )
    
    class Meta:
        verbose_name = 'Kecamatan'
        verbose_name_plural = 'Kecamatan'
        ordering = ['nama']
    
    def __str__(self):
        return self.nama


class CCTV(models.Model):
    """Model untuk menyimpan data CCTV"""
    
    STATUS_CHOICES = [
        (True, 'Aktif'),
        (False, 'Tidak Aktif'),
    ]
    
    nama_lokasi = models.CharField(
        max_length=200,
        verbose_name='Nama Lokasi'
    )
    kecamatan = models.ForeignKey(
        Kecamatan,
        on_delete=models.CASCADE,
        related_name='cctv_list',
        verbose_name='Kecamatan'
    )
    youtube_video_id = models.CharField(
        max_length=50,
        verbose_name='YouTube Video ID',
        help_text='ID video dari URL YouTube (contoh: dQw4w9WgXcQ)'
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='Latitude',
        help_text='Koordinat latitude lokasi CCTV (opsional)'
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='Longitude',
        help_text='Koordinat longitude lokasi CCTV (opsional)'
    )
    is_active = models.BooleanField(
        default=True,
        choices=STATUS_CHOICES,
        verbose_name='Status'
    )
    deskripsi = models.TextField(
        blank=True,
        null=True,
        verbose_name='Deskripsi',
        help_text='Deskripsi tambahan lokasi CCTV (opsional)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Dibuat Pada'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Diperbarui Pada'
    )
    last_status_check = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Terakhir Dicek',
        help_text='Waktu terakhir status video dicek'
    )
    status_check_error = models.TextField(
        blank=True,
        null=True,
        verbose_name='Error Pengecekan',
        help_text='Pesan error jika pengecekan status gagal'
    )
    
    class Meta:
        verbose_name = 'CCTV'
        verbose_name_plural = 'CCTV'
        ordering = ['kecamatan', 'nama_lokasi']
    
    def __str__(self):
        return f"{self.nama_lokasi} ({self.kecamatan.nama})"
    
    @property
    def youtube_embed_url(self):
        """Generate YouTube embed URL"""
        return f"https://www.youtube.com/embed/{self.youtube_video_id}"
    
    @property
    def youtube_watch_url(self):
        """Generate YouTube watch URL"""
        return f"https://www.youtube.com/watch?v={self.youtube_video_id}"
    
    def update_status_from_youtube(self):
        """Update status CCTV berdasarkan ketersediaan video YouTube"""
        from django.utils import timezone
        from .utils import check_youtube_video_status
        
        is_online, error_msg = check_youtube_video_status(self.youtube_video_id)
        
        self.is_active = is_online
        self.last_status_check = timezone.now()
        self.status_check_error = error_msg if error_msg else None
        self.save()
        
        return is_online, error_msg
