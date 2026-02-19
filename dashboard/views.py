"""
Views untuk Dashboard CCTV Lalu Lintas Kota Pontianak
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import CCTV, Kecamatan


def index(request):
    """
    Halaman utama dashboard CCTV
    Menampilkan peta interaktif dan grid view CCTV
    """
    # Ambil data untuk template (semua CCTV, termasuk yang tidak aktif)
    cctv_list = CCTV.objects.all().select_related('kecamatan')
    kecamatan_list = Kecamatan.objects.all()
    
    context = {
        'cctv_list': cctv_list,
        'kecamatan_list': kecamatan_list,
        'total_cctv': cctv_list.count(),
        'total_kecamatan': kecamatan_list.count(),
    }
    
    return render(request, 'dashboard/index.html', context)


def api_cctv_list(request):
    """
    API endpoint untuk mengambil data CCTV dalam format JSON
    Digunakan untuk peta interaktif dan filtering
    """
    # Filter berdasarkan kecamatan jika ada parameter
    kecamatan_id = request.GET.get('kecamatan')
    
    cctv_queryset = CCTV.objects.all().select_related('kecamatan')
    
    if kecamatan_id and kecamatan_id != 'all':
        cctv_queryset = cctv_queryset.filter(kecamatan_id=kecamatan_id)
    
    cctv_data = []
    for cctv in cctv_queryset:
        cctv_data.append({
            'id': cctv.id,
            'nama_lokasi': cctv.nama_lokasi,
            'kecamatan': cctv.kecamatan.nama,
            'kecamatan_id': cctv.kecamatan.id,
            'youtube_video_id': cctv.youtube_video_id,
            'youtube_embed_url': cctv.youtube_embed_url,
            'latitude': float(cctv.latitude) if cctv.latitude else None,
            'longitude': float(cctv.longitude) if cctv.longitude else None,
            'is_active': cctv.is_active,
            'deskripsi': cctv.deskripsi or '',
        })
    
    return JsonResponse({
        'success': True,
        'count': len(cctv_data),
        'data': cctv_data
    })


def api_kecamatan_list(request):
    """
    API endpoint untuk mengambil daftar kecamatan
    """
    kecamatan_list = Kecamatan.objects.all()
    
    data = []
    for kec in kecamatan_list:
        data.append({
            'id': kec.id,
            'nama': kec.nama,
            'jumlah_cctv': kec.cctv_list.filter(is_active=True).count()
        })
    
    return JsonResponse({
        'success': True,
        'count': len(data),
        'data': data
    })


@require_http_methods(["POST"])
def api_refresh_cctv_status(request, cctv_id):
    """
    API endpoint untuk refresh status CCTV tertentu
    """
    try:
        cctv = get_object_or_404(CCTV, id=cctv_id)
        is_online, error_msg = cctv.update_status_from_youtube()
        
        return JsonResponse({
            'success': True,
            'cctv_id': cctv.id,
            'nama_lokasi': cctv.nama_lokasi,
            'is_active': is_online,
            'error_message': error_msg,
            'last_check': cctv.last_status_check.isoformat() if cctv.last_status_check else None
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def api_refresh_all_status(request):
    """
    API endpoint untuk refresh status semua CCTV
    """
    try:
        cctv_list = CCTV.objects.all()
        results = []
        
        for cctv in cctv_list:
            is_online, error_msg = cctv.update_status_from_youtube()
            results.append({
                'id': cctv.id,
                'nama_lokasi': cctv.nama_lokasi,
                'is_active': is_online,
                'error_message': error_msg
            })
        
        online_count = sum(1 for r in results if r['is_active'])
        offline_count = len(results) - online_count
        
        return JsonResponse({
            'success': True,
            'total': len(results),
            'online': online_count,
            'offline': offline_count,
            'results': results
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
