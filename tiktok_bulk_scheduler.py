"""
TikTok Bulk Video Scheduler
This script allows you to bulk schedule video uploads to your TikTok account
using TikTok's Content Posting API.
"""

import os
import json
import csv
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class CustomException(Exception):
    """Custom exception for TikTok scheduler errors"""
    pass


class TikTokScheduler:
    """Main class for handling TikTok video uploads and scheduling"""
    
    def __init__(self, client_key: str, client_secret: str, access_token: str):
        """
        Initialize TikTok Scheduler
        
        Args:
            client_key: TikTok API client key
            client_secret: TikTok API client secret
            access_token: OAuth access token with video.upload scope
        """
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://open.tiktokapis.com/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make API request with error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            CustomException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
            except:
                error_msg += f" - {e.response.text}"
            raise CustomException(error_msg)
        except requests.exceptions.RequestException as e:
            raise CustomException(f"Request failed: {str(e)}")
    
    def initialize_upload(self, video_path: str) -> Dict:
        """
        Initialize video upload to get upload URL
        
        Args:
            video_path: Path to video file
            
        Returns:
            Upload initialization response with upload URL
        """
        if not os.path.exists(video_path):
            raise CustomException(f"Video file not found: {video_path}")
        
        # Get video file size
        file_size = os.path.getsize(video_path)
        
        # Initialize upload
        endpoint = "/post/publish/inbox/video/init/"
        payload = {
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": 10000000,  # 10MB chunks
                "total_chunk_count": (file_size + 9999999) // 10000000
            }
        }
        
        response = self._make_request("POST", endpoint, json=payload)
        return response
    
    def upload_video_chunk(self, upload_url: str, video_path: str, 
                          chunk_number: int, chunk_size: int = 10000000) -> bool:
        """
        Upload a chunk of the video file
        
        Args:
            upload_url: Upload URL from initialization
            video_path: Path to video file
            chunk_number: Current chunk number (0-indexed)
            chunk_size: Size of each chunk in bytes
            
        Returns:
            True if upload successful
        """
        try:
            with open(video_path, 'rb') as f:
                f.seek(chunk_number * chunk_size)
                chunk_data = f.read(chunk_size)
            
            headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes {chunk_number * chunk_size}-{chunk_number * chunk_size + len(chunk_data) - 1}/*"
            }
            
            response = requests.put(upload_url, data=chunk_data, headers=headers)
            response.raise_for_status()
            return True
        except Exception as e:
            raise CustomException(f"Failed to upload chunk {chunk_number}: {str(e)}")
    
    def upload_video(self, video_path: str) -> str:
        """
        Upload complete video file to TikTok
        
        Args:
            video_path: Path to video file
            
        Returns:
            Upload session ID
        """
        print(f"Initializing upload for: {video_path}")
        init_response = self.initialize_upload(video_path)
        
        upload_url = init_response.get("data", {}).get("upload_url")
        upload_session_id = init_response.get("data", {}).get("upload_session_id")
        
        if not upload_url or not upload_session_id:
            raise CustomException("Failed to get upload URL from initialization")
        
        # Upload video in chunks
        file_size = os.path.getsize(video_path)
        chunk_size = 10000000  # 10MB
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        print(f"Uploading {total_chunks} chunk(s)...")
        for chunk_num in range(total_chunks):
            self.upload_video_chunk(upload_url, video_path, chunk_num, chunk_size)
            print(f"Uploaded chunk {chunk_num + 1}/{total_chunks}")
        
        return upload_session_id
    
    def publish_video(self, upload_session_id: str, caption: str, 
                     privacy_level: str = "PUBLIC_TO_EVERYONE",
                     schedule_time: Optional[datetime] = None) -> Dict:
        """
        Publish or schedule a video
        
        Args:
            upload_session_id: Upload session ID from video upload
            caption: Video caption/description
            privacy_level: Privacy setting (PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, etc.)
            schedule_time: Optional datetime to schedule the post
            
        Returns:
            Publish response
        """
        endpoint = "/post/publish/"
        
        payload = {
            "post_info": {
                "title": caption,
                "privacy_level": privacy_level,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_id": upload_session_id
            }
        }
        
        # Add scheduling if provided
        if schedule_time:
            # TikTok API expects Unix timestamp in seconds
            schedule_timestamp = int(schedule_time.timestamp())
            payload["post_info"]["schedule_time"] = schedule_timestamp
        
        response = self._make_request("POST", endpoint, json=payload)
        return response
    
    def schedule_video(self, video_path: str, caption: str, 
                      schedule_time: datetime,
                      privacy_level: str = "PUBLIC_TO_EVERYONE") -> Dict:
        """
        Complete workflow: upload and schedule a video
        
        Args:
            video_path: Path to video file
            caption: Video caption
            schedule_time: When to schedule the post
            privacy_level: Privacy setting
            
        Returns:
            Schedule response
        """
        print(f"\nProcessing video: {os.path.basename(video_path)}")
        print(f"Scheduled for: {schedule_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Upload video
        upload_session_id = self.upload_video(video_path)
        
        # Publish with schedule
        result = self.publish_video(upload_session_id, caption, privacy_level, schedule_time)
        
        print(f"✓ Successfully scheduled video")
        return result


def load_videos_from_csv(csv_path: str) -> List[Dict]:
    """
    Load video information from CSV file
    
    CSV format:
    video_path,caption,schedule_time,privacy_level
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        List of video dictionaries
    """
    videos = []
    
    if not os.path.exists(csv_path):
        raise CustomException(f"CSV file not found: {csv_path}")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            video_path = row.get('video_path', '').strip()
            caption = row.get('caption', '').strip()
            schedule_time_str = row.get('schedule_time', '').strip()
            privacy_level = row.get('privacy_level', 'PUBLIC_TO_EVERYONE').strip()
            
            if not video_path or not caption or not schedule_time_str:
                print(f"Warning: Skipping incomplete row: {row}")
                continue
            
            # Parse schedule time
            try:
                schedule_time = datetime.strptime(schedule_time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    schedule_time = datetime.strptime(schedule_time_str, '%Y-%m-%d %H:%M')
                except ValueError:
                    raise CustomException(f"Invalid schedule_time format: {schedule_time_str}. Use 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM'")
            
            videos.append({
                'video_path': video_path,
                'caption': caption,
                'schedule_time': schedule_time,
                'privacy_level': privacy_level
            })
    
    return videos


def load_videos_from_json(json_path: str) -> List[Dict]:
    """
    Load video information from JSON file
    
    JSON format:
    [
        {
            "video_path": "path/to/video.mp4",
            "caption": "Video caption",
            "schedule_time": "2024-01-15 14:30:00",
            "privacy_level": "PUBLIC_TO_EVERYONE"
        }
    ]
    
    Args:
        json_path: Path to JSON file
        
    Returns:
        List of video dictionaries
    """
    if not os.path.exists(json_path):
        raise CustomException(f"JSON file not found: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos = []
    for item in data:
        schedule_time_str = item.get('schedule_time', '')
        try:
            schedule_time = datetime.strptime(schedule_time_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                schedule_time = datetime.strptime(schedule_time_str, '%Y-%m-%d %H:%M')
            except ValueError:
                raise CustomException(f"Invalid schedule_time format: {schedule_time_str}")
        
        videos.append({
            'video_path': item['video_path'],
            'caption': item['caption'],
            'schedule_time': schedule_time,
            'privacy_level': item.get('privacy_level', 'PUBLIC_TO_EVERYONE')
        })
    
    return videos


def main():
    """Main function to run bulk scheduling"""
    
    # Load configuration
    config_path = "config.json"
    if not os.path.exists(config_path):
        raise CustomException(f"Configuration file not found: {config_path}. Please create it using config.json.example")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    client_key = config.get('client_key')
    client_secret = config.get('client_secret')
    access_token = config.get('access_token')
    input_file = config.get('input_file', 'videos.csv')
    
    if not all([client_key, client_secret, access_token]):
        raise CustomException("Missing required configuration: client_key, client_secret, or access_token")
    
    # Initialize scheduler
    scheduler = TikTokScheduler(client_key, client_secret, access_token)
    
    # Load videos
    print(f"Loading videos from: {input_file}")
    if input_file.endswith('.csv'):
        videos = load_videos_from_csv(input_file)
    elif input_file.endswith('.json'):
        videos = load_videos_from_json(input_file)
    else:
        raise CustomException("Input file must be CSV or JSON format")
    
    print(f"Found {len(videos)} video(s) to schedule\n")
    
    # Process each video
    successful = 0
    failed = 0
    
    for i, video_info in enumerate(videos, 1):
        try:
            print(f"\n[{i}/{len(videos)}] Processing video...")
            scheduler.schedule_video(
                video_path=video_info['video_path'],
                caption=video_info['caption'],
                schedule_time=video_info['schedule_time'],
                privacy_level=video_info.get('privacy_level', 'PUBLIC_TO_EVERYONE')
            )
            successful += 1
            
            # Add delay between uploads to avoid rate limiting
            if i < len(videos):
                print("Waiting 5 seconds before next upload...")
                time.sleep(5)
                
        except CustomException as e:
            print(f"✗ Error: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ Unexpected error: {str(e)}")
            failed += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Bulk scheduling complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"{'='*50}")


if __name__ == "__main__":
    try:
        main()
    except CustomException as e:
        print(f"Error: {str(e)}")
        exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        exit(0)

