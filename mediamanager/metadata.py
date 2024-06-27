from datetime import datetime
import logging
from mediamanager import geo
import os
import PIL.Image
from pymediainfo import MediaInfo
from mediamanager import utils

logger = logging.getLogger("mediamanager")

def get_metadata(path, db, cfg):
    exif_data = None
    try:
        img = PIL.Image.open(path)
        exif_data = img._getexif()
    except PIL.UnidentifiedImageError:
        pass
    except AttributeError:
        pass

    # Get timestamp, date and year
    timestamp = None
    if exif_data:
        timestamp = get_timestamp(exif_data)
    else:
        media_info = get_media_info(path)
        timestamp = media_info.get("creation_date")

    # If neither EXIF or media info is available, resort to using the creation
    # timestamp
    if not timestamp:
        timestamp = get_creation_timestamp(path)

    date = utils.get_date(timestamp)
    year = utils.get_year(timestamp)

    # Get location
    coords = None
    address = None
    if exif_data:
        coords = geo.get_coords(exif_data)
        address = geo.get_address(db, cfg, coords)

    return {
        "path": path,
        "coords": coords,
        "location": address,
        "date": date,
        "year": year
    }


def get_timestamp(exif_data):
    if not exif_data:
        return None

    creation_time_tag_id = 36867
    creation_time_str = exif_data.get(creation_time_tag_id)
    if not creation_time_str:
        return None

    timestamp = datetime.strptime(creation_time_str, "%Y:%m:%d %H:%M:%S")
    return timestamp


def get_creation_timestamp(file_path):
    try:
        # Get the creation time
        creation_time = os.path.getctime(file_path)
        # Get the modification time
        modification_time = os.path.getmtime(file_path)

        # Compare and get the earliest timestamp
        earliest_timestamp = min(creation_time, modification_time)

        # Convert the earliest timestamp to a datetime object
        timestamp = datetime.fromtimestamp(earliest_timestamp)
        return timestamp
    except Exception as e:
        logger.error(e)
        return None


def get_media_info(file_path):
    try:
        media_info = MediaInfo.parse(file_path)
        metadata = {
            'creation_date': None,
            'general': {},
            'video': {},
            'audio': {},
            'image': {},
            'menu': {}
        }

        for track in media_info.tracks:
            if track.track_type == 'General':
                metadata['general']['format'] = track.format
                metadata['general']['file_size'] = track.file_size
                metadata['general']['duration'] = track.duration
                metadata['general']['bit_rate'] = track.overall_bit_rate
                creation_date = track.encoded_date
                if creation_date:
                    date_str = creation_date.replace('UTC ', '')
                    metadata['creation_date'] = datetime.strptime(
                        date_str, '%Y-%m-%d %H:%M:%S')

            elif track.track_type == 'Video':
                metadata['video']['video_codec'] = track.codec_id
                metadata['video']['width'] = track.width
                metadata['video']['height'] = track.height
                metadata['video']['frame_rate'] = track.frame_rate
                metadata['video']['aspect_ratio'] = track.display_aspect_ratio
                metadata['video']['bit_rate'] = track.bit_rate

            elif track.track_type == 'Audio':
                metadata['audio']['audio_codec'] = track.codec_id
                metadata['audio']['sampling_rate'] = track.sampling_rate
                metadata['audio']['channels'] = track.channel_s
                metadata['audio']['bit_rate'] = track.bit_rate
                metadata['audio']['language'] = track.language

            elif track.track_type == 'Image':
                metadata['image']['image_codec'] = track.codec_id
                metadata['image']['image_width'] = track.width
                metadata['image']['image_height'] = track.height

            elif track.track_type == 'Menu':
                metadata['menu']['menu_format'] = track.format

            # Check for GPS data (if available)
            if hasattr(track, 'latitude') and hasattr(track, 'longitude'):
                metadata['gps_latitude'] = track.latitude
                metadata['gps_longitude'] = track.longitude
                if hasattr(track, 'altitude'):
                    metadata['gps_altitude'] = track.altitude

        return metadata
    except Exception as e:
        logger.error(e)
        return None
