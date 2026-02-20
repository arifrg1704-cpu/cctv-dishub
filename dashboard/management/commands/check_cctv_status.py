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
        parser.add_argument(
            '--loop',
            type=int,
            metavar='SECONDS',
            nargs='?',
            const=300,
            help='Jalankan pengecekan terus menerus dengan interval tertentu (default 300 detik/5 menit)',
        )

    def handle(self, *args, **options):
        import time
        from dashboard.utils import check_multiple_videos
        
        video_id = options.get('video_id')
        verbose = options.get('verbose', False)
        loop_interval = options.get('loop')
        
        if loop_interval:
            self.stdout.write(self.style.SUCCESS(f'Starting continuous monitoring (Interval: {loop_interval}s)...'))
            try:
                while True:
                    self._check_all_cctv(video_id, verbose)
                    self.stdout.write(f'Sleeping for {loop_interval} seconds...')
                    time.sleep(loop_interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\nMonitoring stopped by user.'))
        else:
            self._check_all_cctv(video_id, verbose)

    def _check_all_cctv(self, video_id, verbose):
        from dashboard.utils import check_multiple_videos, discover_live_video_by_keyword
        
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
        self.stdout.write(f'\nMengecek status {total} CCTV (' + timezone.now().strftime("%Y-%m-%d %H:%M:%S") + ')...')
        
        # Collect video IDs for batch check
        video_ids = list(cctv_list.values_list('youtube_video_id', flat=True))
        
        # Batch Check (Hemat Quota!)
        results = check_multiple_videos(video_ids)
        
        stats = {'online': 0, 'offline': 0, 'error': 0}
        
        for cctv in cctv_list:
            vid = cctv.youtube_video_id
            is_online, error_msg = results.get(vid, (False, "Check skipped/failed"))
            
            # --- LOGIKA AUTO-DISCOVERY ---
            # Jika video terdeteksi offline DAN memiliki setting discovery (Channel ID & Keyword)
            if not is_online and cctv.youtube_channel_id and cctv.search_keyword:
                self.stdout.write(f'  [Discovery] "{cctv.nama_lokasi}" offline, mencari di channel...')
                new_vid, discovery_error = discover_live_video_by_keyword(cctv.youtube_channel_id, cctv.search_keyword)
                
                if new_vid:
                    self.stdout.write(self.style.SUCCESS(f'  [Found!] "{cctv.nama_lokasi}" ganti ID: {vid} -> {new_vid}'))
                    cctv.youtube_video_id = new_vid
                    is_online = True
                    error_msg = ""
                else:
                    self.stdout.write(f'  [Not Found] {discovery_error}')
            # -----------------------------
            
            # Update fields
            cctv.is_active = is_online
            cctv.last_status_check = timezone.now()
            cctv.status_check_error = error_msg if not is_online else None
            
            update_fields = ['is_active', 'last_status_check', 'status_check_error']
            # Jika video_id berubah (karena discovery), simpan juga
            if cctv.youtube_video_id != vid:
                update_fields.append('youtube_video_id')
                
            cctv.save(update_fields=update_fields)
            
            if is_online:
                stats['online'] += 1
                status_text = self.style.SUCCESS('✓ ONLINE')
            else:
                stats['offline'] += 1
                status_text = self.style.WARNING(f'✗ OFFLINE - {error_msg}')
            
            if verbose:
                self.stdout.write(f'  [{cctv.nama_lokasi}] {status_text}')
                
        # Summary
        self.stdout.write(f'Result: {stats["online"]} Online, {stats["offline"]} Offline')
