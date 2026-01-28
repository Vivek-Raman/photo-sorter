#!/usr/bin/env python3
"""
Photo Sorter - Organizes photos by capture date into yyyy-MM/yyyy-MM-dd folder structure.
"""

import argparse
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS


# Supported photo extensions (case-insensitive)
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif"}


def get_exif_date(file_path: Path) -> datetime | None:
    """
    Extract the capture date from EXIF metadata.
    
    Returns None if EXIF data is unavailable or doesn't contain a date.
    """
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data is None:
                return None
            
            # Build a dict of tag names to values
            exif = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                exif[tag_name] = value
            
            # Try DateTimeOriginal first (when photo was taken), then DateTime
            date_str = exif.get("DateTimeOriginal") or exif.get("DateTime")
            
            if date_str:
                # EXIF date format is typically "YYYY:MM:DD HH:MM:SS"
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except Exception:
        # Any error reading EXIF (corrupt file, unsupported format, etc.)
        pass
    
    return None


def get_photo_date(file_path: Path) -> datetime:
    """
    Get the date for a photo file.
    
    Tries EXIF metadata first, falls back to file modification time.
    """
    # Try EXIF date first
    exif_date = get_exif_date(file_path)
    if exif_date:
        return exif_date
    
    # Fall back to file modification time
    mtime = os.path.getmtime(file_path)
    return datetime.fromtimestamp(mtime)


def is_photo_file(file_path: Path) -> bool:
    """Check if a file is a supported photo format."""
    return file_path.suffix.lower() in PHOTO_EXTENSIONS


def get_photo_files(directory: Path) -> list[Path]:
    """Get all photo files in the top-level of a directory."""
    photos = []
    for item in directory.iterdir():
        if item.is_file() and is_photo_file(item):
            photos.append(item)
    return photos


def organize_photos(directory: Path) -> None:
    """
    Organize all photos in the directory by date.
    
    Creates yyyy-MM/yyyy-MM-dd folder structure and moves photos accordingly.
    """
    photos = get_photo_files(directory)
    
    if not photos:
        print("No photo files found in the directory.")
        return
    
    print(f"Found {len(photos)} photo(s) to process.")
    
    moved_count = 0
    skipped_count = 0
    error_count = 0
    monthly_stats: dict[str, int] = defaultdict(int)
    
    for photo in photos:
        try:
            # Get the photo's date
            photo_date = get_photo_date(photo)
            
            # Create folder structure: yyyy-MM/yyyy-MM-dd
            month_key = photo_date.strftime("%Y-%m")
            month_folder = directory / month_key
            day_folder = month_folder / photo_date.strftime("%Y-%m-%d")
            
            # Create directories if they don't exist
            day_folder.mkdir(parents=True, exist_ok=True)
            
            # Destination path
            dest_path = day_folder / photo.name
            
            # Check for duplicates
            if dest_path.exists():
                print(f"  Skipped (duplicate): {photo.name}")
                skipped_count += 1
                continue
            
            # Move the file
            shutil.move(str(photo), str(dest_path))
            print(f"  Moved: {photo.name} -> {day_folder.relative_to(directory)}/")
            moved_count += 1
            monthly_stats[month_key] += 1
            
        except PermissionError:
            print(f"  Error (permission denied): {photo.name}")
            error_count += 1
        except Exception as e:
            print(f"  Error processing {photo.name}: {e}")
            error_count += 1
    
    # Summary
    print()
    print(f"Complete: {moved_count} moved, {skipped_count} skipped, {error_count} errors")
    
    # Monthly breakdown
    if monthly_stats:
        print()
        print("Photos by month:")
        for month in sorted(monthly_stats.keys()):
            print(f"  {month}: {monthly_stats[month]}")


def main():
    parser = argparse.ArgumentParser(
        description="Organize photos by capture date into yyyy-MM/yyyy-MM-dd folders."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Path to the directory containing photos to organize"
    )
    
    args = parser.parse_args()
    
    # Validate directory
    directory = Path(args.directory).resolve()
    
    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}")
        sys.exit(1)
    
    if not directory.is_dir():
        print(f"Error: Path is not a directory: {directory}")
        sys.exit(1)
    
    print(f"Organizing photos in: {directory}")
    print()
    
    organize_photos(directory)


if __name__ == "__main__":
    main()
