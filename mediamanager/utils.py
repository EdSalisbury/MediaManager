import logging
import os
import shutil
import xxhash

logger = logging.getLogger("mediamanager")

def get_date(timestamp):
    if not timestamp:
        return None
    return timestamp.strftime('%Y-%m-%d')


def get_year(timestamp):
    if not timestamp:
        return None
    return timestamp.strftime('%Y')


def generate_unique_filename(file_path):
    if not os.path.exists(file_path):
        return file_path  # If file doesn't exist, no collision, return original path

    file_name, file_ext = os.path.splitext(file_path)
    counter = 1

    while True:
        new_file_path = f"{file_name}_{counter:03d}{file_ext}"
        if not os.path.exists(new_file_path):
            return new_file_path  # Return the new path if it doesn't exist

        counter += 1


def move_file(path, new_path):
    new_path = generate_unique_filename(new_path)

    logger.info(f"Moving {path} to {new_path}")

    folder = os.path.dirname(new_path)
    os.makedirs(folder, exist_ok=True)

    try:
        shutil.move(path, new_path)
    except Exception as e:
        logger.error(e)
    return True


def get_hash(file_path, chunk_size=65536):
    """Generate xxhash of the specified file."""
    hasher = xxhash.xxh3_64()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
    except Exception:
        return None
    return hasher.hexdigest()
