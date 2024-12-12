import logging
import os
import tempfile
from wand.image import Image

logger = logging.getLogger("mediamanager")

def convert_heic_to_jpeg(heic_file):
    try:
        # Extract directory path and filename without extension
        filename_no_ext = os.path.splitext(os.path.basename(heic_file))[0]

        # Generate JPEG file path in a temp dir
        temp_dir = tempfile.mkdtemp()
        jpeg_file_path = os.path.join(temp_dir, filename_no_ext + '.jpg')

        # Use Wand to convert HEIC to JPEG
        with Image(filename=heic_file) as img:
            img.format = 'jpeg'
            img.save(filename=jpeg_file_path)

        return jpeg_file_path

    except Exception as e:
        logger.error(e)
        raise
