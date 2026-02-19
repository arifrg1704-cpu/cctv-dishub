"""
Django Admin configuration untuk Dashboard CCTV
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Kecamatan, CCTV
from .forms import AdminLoginForm

# Admin Customization Branding
admin.site.site_header = "Dashboard CCTV Pontianak"
admin.site.site_title = "Admin Dishub Pontianak"
admin.site.index_title = "Manajemen CCTV Lalu Lintas"
admin.site.login_form = AdminLoginForm


@admin.register(Kecamatan)
class KecamatanAdmin(admin.ModelAdmin):
    """Admin untuk model Kecamatan"""
    
    list_display = ['nama', 'jumlah_cctv', 'created_at']
    search_fields = ['nama']
    ordering = ['nama']
    
    def jumlah_cctv(self, obj):
        """Hitung jumlah CCTV di kecamatan ini"""
        return obj.cctv_list.count()
    jumlah_cctv.short_description = 'Jumlah CCTV'


@admin.register(CCTV)
class CCTVAdmin(admin.ModelAdmin):
    """Admin untuk model CCTV"""
    
    list_display = [
        'nama_lokasi', 
        'kecamatan', 
        'status_badge',
        'is_active',
        'youtube_video_id',
        'koordinat',
        'last_check_info',
        'updated_at'
    ]
    list_filter = ['kecamatan', 'is_active']
    search_fields = ['nama_lokasi', 'deskripsi', 'youtube_video_id']
    ordering = ['kecamatan', 'nama_lokasi']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'last_status_check', 'status_check_error']
    actions = ['refresh_status_action']
    
    fieldsets = (
        ('Informasi Lokasi', {
            'fields': ('nama_lokasi', 'kecamatan', 'deskripsi')
        }),
        ('Konfigurasi Video', {
            'fields': ('youtube_video_id',)
        }),
        ('Koordinat GPS', {
            'fields': ('latitude', 'longitude'),
            'description': 'Koordinat untuk menampilkan lokasi di peta'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Informasi Waktu', {
            'fields': ('created_at', 'updated_at', 'last_status_check', 'status_check_error'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Tampilkan status dengan badge berwarna"""
        if obj.is_active:
            return '🟢 Aktif'
        return '🔴 Tidak Aktif'
    status_badge.short_description = 'Status'
    
    def koordinat(self, obj):
        """Tampilkan koordinat dalam format singkat"""
        return f"{obj.latitude}, {obj.longitude}"
    koordinat.short_description = 'Koordinat'
    
    def last_check_info(self, obj):
        """Tampilkan informasi terakhir pengecekan status"""
        if not obj.last_status_check:
            return format_html('<span style="color: #999;">Belum pernah dicek</span>')
        
        now = timezone.now()
        diff = now - obj.last_status_check
        
        if diff.total_seconds() < 60:
            time_ago = 'Baru saja'
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            time_ago = f'{minutes} menit lalu'
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            time_ago = f'{hours} jam lalu'
        else:
            days = int(diff.total_seconds() / 86400)
            time_ago = f'{days} hari lalu'
        
        if obj.status_check_error:
            return format_html(
                '<span style="color: #d63031;" title="{}">⚠️ {}</span>',
                obj.status_check_error,
                time_ago
            )
        else:
            return format_html(
                '<span style="color: #00b894;" title="{}">✓ {}</span>',
                obj.last_status_check.strftime('%Y-%m-%d %H:%M:%S'),
                time_ago
            )
    last_check_info.short_description = 'Terakhir Dicek'
    
    def refresh_status_action(self, request, queryset):
        """Admin action untuk refresh status CCTV yang dipilih"""
        updated = 0
        errors = 0
        
        for cctv in queryset:
            try:
                cctv.update_status_from_youtube()
                updated += 1
            except Exception as e:
                errors += 1
        
        if errors == 0:
            self.message_user(
                request,
                f'Berhasil refresh status {updated} CCTV'
            )
        else:
            self.message_user(
                request,
                f'Refresh selesai: {updated} berhasil, {errors} error',
                level='WARNING'
            )
    refresh_status_action.short_description = 'Refresh status dari YouTube'
