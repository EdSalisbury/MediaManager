# MediaManager

MediaManager is a powerful and flexible media management tool designed to handle both photo and video files. It provides functionalities such as metadata extraction, duplicate detection, and file organization.

## Features

- **Metadata Extraction**: Extracts metadata from both photo and video files.
- **Duplicate Detection**: Identifies and manages duplicate files.
- **File Organization**: Organizes files based on metadata such as date, location, and more.
- **HEIC to JPEG Conversion**: Converts HEIC image files to JPEG format.

## Installation

To install MediaManager, clone the repository and install the required dependencies:

```bash
git clone https://github.com/edsalisbury/mediamanager.git
cd mediamanager
pip install -r requirements.txt
sudo cp bin/mediamanger /usr/local/bin
```

## Usage

MediaManager can be run from the command line with various options. Here are some examples:

### Import Files

```bash
mediamanager --import-files /path/to/media
```

### Move Duplicates

```bash
mediamanager --move-duplicates
```

### Set Maximum Number of Workers

```bash
mediamanager --max_workers 8
```

## Configuration

MediaManager uses a configuration file named `mediamanager.cfg.json` located in the root directory. Below is an example configuration:

```json
{
    "main_dir": "/path/to/main/directory",
    "duplicate_dir": "/path/to/duplicate/directory",
    "skip_files": ["desktop.ini"],
    "locations": {
        "house_number road, city, state": "Custom Location Name"
    }
}
```

- `main_dir`: The main directory where media files are stored.
- `duplicate_dir`: The directory where duplicate files will be moved.
- `skip_files`: A list of files to skip during processing.
- `locations`: Custom location names based on address strings.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) file for guidelines on how to contribute to this project.

## Authors

- **Ed Salisbury** - *Initial work* - [edsalisbury](https://github.com/edsalisbury)

See also the list of [contributors](https://github.com/edsalisbury/mediamanager/CONTRIBUTORS.md) who participated in this project.

## Acknowledgments

- ChatGPT

## Contact

If you have any questions or suggestions, feel free to open an issue or reach out directly.
