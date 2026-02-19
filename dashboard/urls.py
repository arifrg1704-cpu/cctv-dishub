"""
URL routing untuk Dashboard app
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Halaman utama
    path('', views.index, name='index'),
    
    # API endpoints
    path('api/cctv/', views.api_cctv_list, name='api_cctv_list'),
    path('api/kecamatan/', views.api_kecamatan_list, name='api_kecamatan_list'),
    path('api/cctv/<int:cctv_id>/refresh-status/', views.api_refresh_cctv_status, name='api_refresh_cctv_status'),
    path('api/cctv/refresh-all-status/', views.api_refresh_all_status, name='api_refresh_all_status'),
]
