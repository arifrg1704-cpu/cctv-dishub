"""
Management command untuk mengisi data dummy CCTV Kota Pontianak
"""

from django.core.management.base import BaseCommand
from dashboard.models import Kecamatan, CCTV


class Command(BaseCommand):
    help = 'Mengisi database dengan data dummy CCTV Kota Pontianak'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip jika data sudah ada',
        )
    
    def handle(self, *args, **options):
        skip_existing = options['skip_existing']
        
        # Cek apakah data sudah ada
        if skip_existing and CCTV.objects.exists():
            self.stdout.write(
                self.style.WARNING('Data sudah ada, skip seeding.')
            )
            return
        
        self.stdout.write('Memulai seeding data...')
        
        # Data Kecamatan Kota Pontianak
        kecamatan_data = [
            'Pontianak Utara',
            'Pontianak Timur',
            'Pontianak Selatan',
            'Pontianak Barat',
            'Pontianak Kota',
            'Pontianak Tenggara',
        ]
        
        # Buat atau ambil kecamatan
        kecamatan_objects = {}
        for nama in kecamatan_data:
            kec, created = Kecamatan.objects.get_or_create(nama=nama)
            kecamatan_objects[nama] = kec
            if created:
                self.stdout.write(f'  + Kecamatan: {nama}')
        
        # Data CCTV dummy dengan lokasi nyata di Pontianak
        # Koordinat diambil dari area Kota Pontianak
        cctv_data = [
            # Pontianak Kota
            {
                'nama_lokasi': 'Simpang Jl. Tanjungpura - Jl. Diponegoro',
                'kecamatan': 'Pontianak Kota',
                'youtube_video_id': 'LDU_Txk06tM',  # Placeholder - ganti dengan ID asli
                'latitude': -0.0226,
                'longitude': 109.3425,
                'deskripsi': 'Persimpangan utama di pusat kota'
            },
            {
                'nama_lokasi': 'Bundaran Untan',
                'kecamatan': 'Pontianak Kota',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0456,
                'longitude': 109.3524,
                'deskripsi': 'Area bundaran depan Universitas Tanjungpura'
            },
            {
                'nama_lokasi': 'Jl. Gajah Mada (Depan Mall)',
                'kecamatan': 'Pontianak Kota',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0312,
                'longitude': 109.3389,
                'deskripsi': 'Kawasan pusat perbelanjaan'
            },
            
            # Pontianak Selatan
            {
                'nama_lokasi': 'Simpang Jl. Ahmad Yani - Jl. Sultan Abdurrahman',
                'kecamatan': 'Pontianak Selatan',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0523,
                'longitude': 109.3456,
                'deskripsi': 'Persimpangan padat di Pontianak Selatan'
            },
            {
                'nama_lokasi': 'Jl. Veteran (Depan RSUD)',
                'kecamatan': 'Pontianak Selatan',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0478,
                'longitude': 109.3512,
                'deskripsi': 'Area rumah sakit daerah'
            },
            {
                'nama_lokasi': 'Terminal Batu Layang',
                'kecamatan': 'Pontianak Selatan',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0612,
                'longitude': 109.3389,
                'deskripsi': 'Terminal bus utama'
            },
            
            # Pontianak Utara
            {
                'nama_lokasi': 'Jl. Khatulistiwa (Tugu Khatulistiwa)',
                'kecamatan': 'Pontianak Utara',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': 0.0015,
                'longitude': 109.3227,
                'deskripsi': 'Area wisata Tugu Khatulistiwa'
            },
            {
                'nama_lokasi': 'Jembatan Landak',
                'kecamatan': 'Pontianak Utara',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0089,
                'longitude': 109.3298,
                'deskripsi': 'Jembatan penyeberangan utama'
            },
            {
                'nama_lokasi': 'Simpang Jl. Gusti Situt Mahmud',
                'kecamatan': 'Pontianak Utara',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0056,
                'longitude': 109.3189,
                'deskripsi': 'Persimpangan kawasan industri'
            },
            
            # Pontianak Timur
            {
                'nama_lokasi': 'Jl. Sutan Syahrir',
                'kecamatan': 'Pontianak Timur',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0334,
                'longitude': 109.3567,
                'deskripsi': 'Jalan utama Pontianak Timur'
            },
            {
                'nama_lokasi': 'Pasar Flamboyan',
                'kecamatan': 'Pontianak Timur',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0289,
                'longitude': 109.3534,
                'deskripsi': 'Area pasar tradisional'
            },
            
            # Pontianak Barat
            {
                'nama_lokasi': 'Jl. Kom Yos Sudarso',
                'kecamatan': 'Pontianak Barat',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0198,
                'longitude': 109.3234,
                'deskripsi': 'Jalan utama menuju pelabuhan'
            },
            {
                'nama_lokasi': 'Pelabuhan Pontianak',
                'kecamatan': 'Pontianak Barat',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0156,
                'longitude': 109.3156,
                'deskripsi': 'Area pelabuhan utama'
            },
            {
                'nama_lokasi': 'Jl. Pak Kasih',
                'kecamatan': 'Pontianak Barat',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0234,
                'longitude': 109.3289,
                'deskripsi': 'Kawasan perkantoran'
            },
            
            # Pontianak Tenggara
            {
                'nama_lokasi': 'Jl. Husein Hamzah',
                'kecamatan': 'Pontianak Tenggara',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0567,
                'longitude': 109.3623,
                'deskripsi': 'Jalan utama Pontianak Tenggara'
            },
            {
                'nama_lokasi': 'Simpang Jl. Ampera',
                'kecamatan': 'Pontianak Tenggara',
                'youtube_video_id': 'LDU_Txk06tM',
                'latitude': -0.0623,
                'longitude': 109.3578,
                'deskripsi': 'Persimpangan kawasan perumahan'
            },
        ]
        
        # Buat CCTV
        created_count = 0
        for data in cctv_data:
            kecamatan = kecamatan_objects[data['kecamatan']]
            
            cctv, created = CCTV.objects.get_or_create(
                nama_lokasi=data['nama_lokasi'],
                defaults={
                    'kecamatan': kecamatan,
                    'youtube_video_id': data['youtube_video_id'],
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'deskripsi': data['deskripsi'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  + CCTV: {data["nama_lokasi"]}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding selesai! '
                f'{len(kecamatan_data)} kecamatan, '
                f'{created_count} CCTV baru ditambahkan.'
            )
        )
