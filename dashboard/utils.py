"""
Utility functions untuk Dashboard CCTV
"""


import requests
import logging
from typing import Tuple
from django.conf import settings

logger = logging.getLogger(__name__)


def check_youtube_video_status(video_id: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    Cek status video YouTube (terutama live stream).
    
    Menggunakan YouTube Data API v3 jika API Key tersedia di settings.YOUTUBE_API_KEY.
    Jika tidak, fallback ke metode oEmbed (kurang akurat untuk status live).
    
    Args:
        video_id: YouTube video ID
        timeout: Timeout untuk request dalam detik (default: 10)
    
    Returns:
        Tuple[bool, str]: (is_online, error_message)
        - is_online: True jika video sedang live, False jika tidak
        - error_message: Pesan error atau status stream
    """
    if not video_id or not video_id.strip():
        return False, "Video ID kosong"
    
    # Prioritaskan menggunakan YouTube Data API jika Key tersedia
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    
    if api_key:
        return _check_with_data_api(video_id, api_key, timeout)
    else:
        logger.warning("YOUTUBE_API_KEY tidak ditemukan. Menggunakan fallback oEmbed (kurang akurat).")
        return _check_with_oembed(video_id, timeout)


def _check_with_data_api(video_id: str, api_key: str, timeout: int) -> Tuple[bool, str]:
    """Internal helper: Cek status menggunakan YouTube Data API v3"""
    api_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'id': video_id,
        'key': api_key,
        'part': 'snippet',
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                return False, "Video tidak ditemukan atau private"
            
            snippet = items[0].get('snippet', {})
            live_broadcast_content = snippet.get('liveBroadcastContent', 'none')
            title = snippet.get('title', 'Unknown')
            
            # liveBroadcastContent values: 'live', 'upcoming', 'none'
            if live_broadcast_content == 'live':
                logger.info(f"API: Video {video_id} is LIVE: {title}")
                return True, ""
            elif live_broadcast_content == 'upcoming':
                logger.info(f"API: Video {video_id} is UPCOMING: {title}")
                return False, "Siaran belum dimulai (Upcoming)"
            else:
                logger.info(f"API: Video {video_id} is NOT LIVE (VOD/Offline): {title}")
                return False, "Siaran berakhir atau offline"
                
        elif response.status_code == 403:
            logger.error(f"API Key Error/Quota Exceeded for video {video_id}")
            return False, "API Key Error atau Kuota Habis"
        elif response.status_code == 404:
            return False, "Video tidak ditemukan"
        else:
            logger.error(f"API Error {response.status_code} for video {video_id}")
            return False, f"API Error: {response.status_code}"
            
    except Exception as e:
        logger.error(f"Exception checks video {video_id} with API: {str(e)}")
        # Jika API gagal total (koneksi putus dll), jangan fallback ke oEmbed karena hasilnya bisa misleading
        # Lebih baik gagal daripada "False Positive"
        return False, f"Error koneksi API: {str(e)}"


def _check_with_oembed(video_id: str, timeout: int) -> Tuple[bool, str]:
    """Internal helper: Fallback cek status menggunakan oEmbed (hanya cek ketersediaan umum)"""
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    
    try:
        response = requests.get(oembed_url, timeout=timeout)
        
        if response.status_code == 200:
            # PENTING: oEmbed tidak bisa membedakan Live vs Offline (VOD)
            # Selama videonya publik, dia akan return 200 OK.
            # Ini sumber ketidakuratan yang lama.
            data = response.json()
            logger.info(f"oEmbed: Video {video_id} available: {data.get('title', 'Unknown')}")
            return True, ""  # Diasumsikan aktif, walau mungkin VOD
        
        elif response.status_code == 404:
            return False, "Video tidak ditemukan, private, atau telah dihapus"
        elif response.status_code == 401:
            return False, "Video private atau restricted"
        else:
            return False, f"HTTP Error {response.status_code}"
            
    except Exception as e:
        logger.error(f"oEmbed error for video {video_id}: {str(e)}")
        return False, f"Error: {str(e)}"


def check_multiple_videos(video_ids: list, timeout: int = 10) -> dict:
    """
    Cek status beberapa video sekaligus.
    Optimasi: Jika menggunakan API Key, bisa request batch hingga 50 ID sekaligus.
    """
    if not video_ids:
        return {}
        
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    results = {}
    
    # Jika pakai API Key, gunakan fitur batch request v3/videos
    if api_key:
        # Chunk video_ids into batches of 50 (max limit youtube api)
        chunk_size = 50
        for i in range(0, len(video_ids), chunk_size):
            chunk = video_ids[i:i + chunk_size]
            ids_string = ','.join(chunk)
            
            api_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'id': ids_string,
                'key': api_key,
                'part': 'snippet',
            }
            
            try:
                response = requests.get(api_url, params=params, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    items = {item['id']: item for item in data.get('items', [])}
                    
                    # Process each ID in this chunk
                    for vid in chunk:
                        item = items.get(vid)
                        if item:
                            snippet = item.get('snippet', {})
                            live_status = snippet.get('liveBroadcastContent', 'none')
                            
                            if live_status == 'live':
                                results[vid] = (True, "")
                            elif live_status == 'upcoming':
                                results[vid] = (False, "Siaran belum dimulai (Upcoming)")
                            else:
                                results[vid] = (False, "Siaran berakhir atau offline")
                        else:
                            results[vid] = (False, "Video tidak ditemukan atau private")
                else:
                    # Jika batch request gagal, fallback check satu-satu pake error message
                    logger.error(f"Batch API Error {response.status_code}")
                    for vid in chunk:
                        results[vid] = (False, f"Batch API Error {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Batch API Exception: {str(e)}")
                for vid in chunk:
                    results[vid] = (False, f"Error: {str(e)}")
                    
        return results

    else:
        # Fallback loop satu-satu pake oEmbed
        for video_id in video_ids:
            is_online, error_msg = check_youtube_video_status(video_id, timeout)
            results[video_id] = (is_online, error_msg)
        
        return results
