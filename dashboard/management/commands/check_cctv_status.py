"""
Django management command untuk mengecek status semua CCTV
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import CCTV
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cek status semua CCTV berdasarkan ketersediaan video YouTube'

    def add_arguments(self, parser):
        parser.add_argument(
            '--video-id',
            type=str,
            help='Cek status untuk video ID tertentu saja',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Tampilkan output detail',
        )

    def handle(self, *args, **options):
        video_id = options.get('video_id')
        verbose = options.get('verbose', False)
        
        # Filter CCTV yang akan dicek
        if video_id:
            cctv_list = CCTV.objects.filter(youtube_video_id=video_id)
            if not cctv_list.exists():
                self.stdout.write(
                    self.style.ERROR(f'Tidak ada CCTV dengan video ID: {video_id}')
                )
                return
        else:
            cctv_list = CCTV.objects.all()
        
        total = cctv_list.count()
        self.stdout.write(f'\nMengecek status {total} CCTV...\n')
        
        # Statistik
        stats = {
            'online': 0,
            'offline': 0,
            'error': 0,
        }
        
        # Cek setiap CCTV
        for idx, cctv in enumerate(cctv_list, 1):
            if verbose:
                self.stdout.write(f'[{idx}/{total}] Mengecek: {cctv.nama_lokasi}...')
            
            try:
                is_online, error_msg = cctv.update_status_from_youtube()
                
                if is_online:
                    stats['online'] += 1
                    status_text = self.style.SUCCESS('✓ ONLINE')
                else:
                    stats['offline'] += 1
                    status_text = self.style.WARNING(f'✗ OFFLINE - {error_msg}')
                
                if verbose:
                    self.stdout.write(f'  {status_text}')
                    self.stdout.write(f'  Video ID: {cctv.youtube_video_id}')
                    self.stdout.write(f'  Kecamatan: {cctv.kecamatan.nama}\n')
                
            except Exception as e:
                stats['error'] += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ ERROR: {str(e)}')
                )
                logger.error(f'Error checking CCTV {cctv.id}: {str(e)}')
        
        # Tampilkan ringkasan
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'\n✓ Pengecekan selesai!\n'))
        self.stdout.write(f'Total CCTV dicek: {total}')
        self.stdout.write(self.style.SUCCESS(f'Online: {stats["online"]}'))
        self.stdout.write(self.style.WARNING(f'Offline: {stats["offline"]}'))
        if stats['error'] > 0:
            self.stdout.write(self.style.ERROR(f'Error: {stats["error"]}'))
        self.stdout.write(f'\nWaktu: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write('='*50 + '\n')
