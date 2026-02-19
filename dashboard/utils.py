"""
Utility functions untuk Dashboard CCTV
"""

import requests
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def check_youtube_video_status(video_id: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    Cek apakah video YouTube sedang online/tersedia menggunakan oEmbed API.
    
    Args:
        video_id: YouTube video ID
        timeout: Timeout untuk request dalam detik (default: 10)
    
    Returns:
        Tuple[bool, str]: (is_online, error_message)
        - is_online: True jika video tersedia, False jika tidak
        - error_message: Pesan error jika ada, string kosong jika tidak ada error
    
    Examples:
        >>> check_youtube_video_status('dQw4w9WgXcQ')
        (True, '')
        >>> check_youtube_video_status('invalid_video_id')
        (False, 'Video tidak ditemukan atau private')
    """
    if not video_id or not video_id.strip():
        return False, "Video ID kosong"
    
    # YouTube oEmbed API endpoint
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    
    try:
        response = requests.get(oembed_url, timeout=timeout)
        
        if response.status_code == 200:
            # Video tersedia dan bisa diakses
            data = response.json()
            logger.info(f"Video {video_id} online: {data.get('title', 'Unknown')}")
            return True, ""
        
        elif response.status_code == 404:
            # Video tidak ditemukan, private, atau dihapus
            logger.warning(f"Video {video_id} tidak tersedia (404)")
            return False, "Video tidak ditemukan, private, atau telah dihapus"
        
        elif response.status_code == 401:
            # Unauthorized - video mungkin private
            logger.warning(f"Video {video_id} private atau restricted (401)")
            return False, "Video private atau restricted"
        
        else:
            # Status code lain yang tidak diharapkan
            logger.error(f"Video {video_id} status code tidak dikenal: {response.status_code}")
            return False, f"HTTP Error {response.status_code}"
    
    except requests.exceptions.Timeout:
        logger.error(f"Timeout saat mengecek video {video_id}")
        return False, "Timeout - koneksi terlalu lama"
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error saat mengecek video {video_id}")
        return False, "Gagal terhubung ke YouTube"
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error untuk video {video_id}: {str(e)}")
        return False, f"Error: {str(e)}"
    
    except Exception as e:
        logger.error(f"Unexpected error untuk video {video_id}: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def check_multiple_videos(video_ids: list, timeout: int = 10) -> dict:
    """
    Cek status beberapa video sekaligus.
    
    Args:
        video_ids: List of YouTube video IDs
        timeout: Timeout untuk setiap request dalam detik
    
    Returns:
        dict: Dictionary dengan video_id sebagai key dan tuple (is_online, error_message) sebagai value
    
    Examples:
        >>> check_multiple_videos(['dQw4w9WgXcQ', 'invalid_id'])
        {'dQw4w9WgXcQ': (True, ''), 'invalid_id': (False, 'Video tidak ditemukan')}
    """
    results = {}
    
    for video_id in video_ids:
        is_online, error_msg = check_youtube_video_status(video_id, timeout)
        results[video_id] = (is_online, error_msg)
    
    return results
