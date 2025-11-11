# TikTok Bulk Video Scheduler

A Python script to bulk schedule and upload videos to your TikTok account using TikTok's official Content Posting API.

## Features

- ✅ Bulk upload and schedule multiple videos
- ✅ Support for CSV and JSON input formats
- ✅ Configurable privacy settings
- ✅ Automatic chunked upload for large videos
- ✅ Error handling and progress tracking
- ✅ Rate limiting protection

## Prerequisites

1. **TikTok Developer Account**: You need to register as a developer on [TikTok's Developer Portal](https://developers.tiktok.com/)
2. **API Credentials**: 
   - Create an application to get `client_key` and `client_secret`
   - Obtain OAuth access token with `video.upload` scope
3. **Python 3.7+**: Make sure Python is installed on your system

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Setup

### 1. Get TikTok API Credentials

1. Go to [TikTok Developer Portal](https://developers.tiktok.com/)
2. Create a new application
3. Note down your `client_key` and `client_secret`
4. Set up OAuth 2.0 and obtain an access token with `video.upload` scope

### 2. Configure the Script

1. Copy the example configuration file:
```bash
copy config.json.example config.json
```

2. Edit `config.json` and fill in your credentials:
```json
{
  "client_key": "your_client_key_here",
  "client_secret": "your_client_secret_here",
  "access_token": "your_access_token_here",
  "input_file": "videos.csv"
}
```

### 3. Prepare Your Video List

You can use either CSV or JSON format to list your videos.

#### CSV Format

Create a `videos.csv` file with the following columns:

```csv
video_path,caption,schedule_time,privacy_level
videos/video1.mp4,Check out this amazing video! #fyp #viral,2024-01-15 14:30:00,PUBLIC_TO_EVERYONE
videos/video2.mp4,Another great video! #trending,2024-01-15 18:00:00,PUBLIC_TO_EVERYONE
```

**Columns:**
- `video_path`: Path to your video file (relative or absolute)
- `caption`: Video caption/description (can include hashtags)
- `schedule_time`: When to schedule the post (format: `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD HH:MM`)
- `privacy_level`: Privacy setting (optional, defaults to `PUBLIC_TO_EVERYONE`)
  - `PUBLIC_TO_EVERYONE`: Public
  - `MUTUAL_FOLLOW_FRIENDS`: Only mutual followers
  - `SELF_ONLY`: Only you

#### JSON Format

Create a `videos.json` file:

```json
[
  {
    "video_path": "videos/video1.mp4",
    "caption": "Check out this amazing video! #fyp #viral",
    "schedule_time": "2024-01-15 14:30:00",
    "privacy_level": "PUBLIC_TO_EVERYONE"
  }
]
```

## Usage

Run the script:

```bash
python tiktok_bulk_scheduler.py
```

The script will:
1. Load videos from your input file (CSV or JSON)
2. Upload each video to TikTok
3. Schedule them according to your specified times
4. Display progress and results

## Example Output

```
Loading videos from: videos.csv
Found 3 video(s) to schedule

[1/3] Processing video...
Processing video: video1.mp4
Scheduled for: 2024-01-15 14:30:00
Initializing upload for: videos/video1.mp4
Uploading 1 chunk(s)...
Uploaded chunk 1/1
✓ Successfully scheduled video
Waiting 5 seconds before next upload...

[2/3] Processing video...
...

==================================================
Bulk scheduling complete!
Successful: 3
Failed: 0
==================================================
```

## Privacy Levels

- `PUBLIC_TO_EVERYONE`: Video is public
- `MUTUAL_FOLLOW_FRIENDS`: Only visible to mutual followers
- `SELF_ONLY`: Only visible to you

## Troubleshooting

### Authentication Errors

- Make sure your access token is valid and has the `video.upload` scope
- Tokens expire, so you may need to refresh them periodically

### Upload Errors

- Check that video files exist and are accessible
- Ensure video format is supported by TikTok (MP4 recommended)
- Check file size limits (TikTok has upload size limits)

### Rate Limiting

- The script includes a 5-second delay between uploads
- If you encounter rate limits, increase the delay in the script

## Important Notes

⚠️ **Compliance**: Make sure your automation complies with TikTok's Terms of Service and Community Guidelines.

⚠️ **Rate Limits**: TikTok has rate limits on API calls. Don't schedule too many videos at once.

⚠️ **Video Requirements**: 
- Supported formats: MP4, MOV
- Maximum file size: Check TikTok's current limits
- Recommended aspect ratio: 9:16 (vertical)

## API Documentation

For more details on TikTok's Content Posting API, visit:
- [TikTok Developer Portal](https://developers.tiktok.com/)
- [Content Posting API Reference](https://developers.tiktok.com/doc/content-posting-api-reference-upload-video)

## License

This script is provided as-is for educational and personal use.

## Support

For issues related to:
- **TikTok API**: Contact TikTok Developer Support
- **Script bugs**: Check the error messages and ensure all configurations are correct

