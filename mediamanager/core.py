from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import json
import logging
import os
import shutil
import traceback
from mediamanager import metadata, media, utils

from localdb import LocalDB

logger = logging.getLogger("mediamanager")


class MediaManager:
    def __init__(self):
        self.cfg = None
        self.db = None

    def init_db(self):
        self.db = LocalDB(self.cfg.get("database_file"), "sqlite3")
        self.db.__enter__()

    def get_cfg_path(self):
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, f".mediamanager.cfg.json")

    def load_cfg(self):
        cfg_file = self.get_cfg_path()
        try:
            with open(cfg_file, "r") as cfg_file:
                self.cfg = json.load(cfg_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {cfg_file}")

    def save_cfg(self, config):
        cfg_file = self.get_cfg_path()
        with open(cfg_file, "w") as file:
            json.dump(config, file, indent=4)
        self.cfg = self.load_cfg()

    def move_to_duplicate(self, path):
        stripped_path = path.lstrip(self.cfg.get("media_directory"))
        new_path = os.path.join(self.cfg.get("duplicate_directory"), stripped_path)
        return utils.move_file(path, new_path)

    def copy_file(self, path):
        md = metadata.get_metadata(path, self.db, self.cfg)

        new_folder = md.get("date")
        if md.get("location"):
            new_folder += f" - {md.get('location')}"

        filename = os.path.basename(path)
        new_path = os.path.join(
            self.cfg.get("media_directory"), md.get("year"), new_folder, filename
        )
        new_path = utils.generate_unique_filename(new_path)

        folder = os.path.dirname(new_path)

        os.makedirs(folder, exist_ok=True)

        logger.info(f"Copying {path} to {new_path}")
        try:
            shutil.copy(path, new_path)
            return new_path
        except Exception as e:
            logger.error(e)
            return None

    def process_file(self, path, move_duplicates=False):
        try:
            # Skip files
            filename = os.path.basename(path)
            if filename in self.cfg.get("skip_files"):
                logger.debug(f"Skipping {path}")
                return True

            logger.debug(f"Processing file {path}")
            hash = utils.get_hash(path)
            db_path = self.db.load_value(hash)
            if db_path:
                logger.debug(f"Record found for {path} ({hash})")
                if os.path.isfile(db_path):
                    if path == db_path:
                        return True
                    else:
                        logger.info(
                            f"Duplicate detected for {path} (original is {db_path})"
                        )
                        if move_duplicates:
                            return self.move_to_duplicate(path)
                        else:
                            return True
                else:
                    logger.debug(f"Replacing record for {db_path} ({hash})")
                    return self.db.save_value(hash, path)
            else:
                logger.debug(f"Adding record for {path} ({hash})")
                return self.db.save_value(hash, path)
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
            # Log the full traceback for debugging
            logger.error(traceback.format_exc())
            return False

    def import_file(self, path):
        try:
            # Skip files
            filename = os.path.basename(path)
            if filename in self.cfg.get("skip_files"):
                logger.debug(f"Skipping {path}")
                return True

            # Convert HEIC to JPEG
            if filename.upper().endswith(".HEIC"):
                logger.info(f"Converting {path} to JPEG")
                path = media.convert_heic_to_jpeg(path)
                if path:
                    return self.import_file(path)
                else:
                    return True

            logger.debug(f"Analyzing file {path}")
            hash = utils.get_hash(path)
            db_path = self.db.load_value(hash)
            if db_path and os.path.isfile(db_path):
                logger.info(f"File has already been imported {path} ({hash}) {db_path}")
                return True
            else:
                logger.info(f"Importing file {path} ({hash})")
                new_path = self.copy_file(path)
                return self.db.save_value(hash, new_path)
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
            # Log the full traceback for debugging
            logger.error(traceback.format_exc())
            return False

    def process_dir(
        self, folder, max_workers=4, import_files=False, move_duplicates=False
    ):
        logger.info(f"Analyzing directory {folder}.")
        paths = os.listdir(folder)
        files = list()
        dirs = list()
        for file in paths:
            path = os.path.join(folder, file)
            if os.path.isfile(path):
                files.append(path)
            elif os.path.isdir(path):
                dirs.append(path)

        for folder in dirs:
            self.process_dir(
                folder,
                max_workers=max_workers,
                import_files=import_files,
                move_duplicates=move_duplicates,
            )

        mtime = os.path.getmtime(folder)
        last_modified = self.db.load_value(folder)
        if import_files or not last_modified or mtime > float(last_modified):
            logger.info(f"Processing files in {folder}.")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                if import_files:
                    partial_process_file = partial(self.import_file)
                else:
                    partial_process_file = partial(
                        self.process_file, move_duplicates=move_duplicates
                    )

                futures = [
                    executor.submit(partial_process_file, file) for file in files
                ]

                for future in as_completed(futures):
                    try:
                        result = future.result()  # Wait for each future to complete
                        if not result:
                            logger.error(
                                f"Processing failed for file: {future.exception()}"
                            )
                    except Exception as e:
                        logger.error(f"Error processing file: {e}")
                        logger.error(traceback.format_exc())

            self.db.save_value(folder, str(mtime))
            logger.info(f"Completed processing directory {folder}.")
        else:
            logger.debug(f"Skipping processing for {folder}.")
