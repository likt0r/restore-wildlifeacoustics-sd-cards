#!/usr/bin/python
"""
Recursively read all WAV files in a directory, extract WAMD metadata, 
and rename the files based on the metadata. Additionally, concatenate
all TXT files found into a single report.txt in the target directory.

usage::

    $> rename_wav_files.py SOURCE_DIRECTORY TARGET_DIRECTORY [--move] [--group-by-month]
"""

import os
import sys
import shutil
import traceback
from read_wa_metadata import read_wildlife_acoustics_metadata

def rename_wav_file(file_path, metadata, target_root_dir, move=False, group_by_month=False):
    """Rename and move/copy the WAV file based on its metadata."""
    prefix = metadata.get('prefix', 'UNKNOWN')
    timestamp = metadata.get('timestamp')
    if timestamp:
        date_str = timestamp.strftime('%Y%m%d')
        time_str = timestamp.strftime('%H%M%S')
        month_str = timestamp.strftime('%Y%m')
        new_file_name = f"{prefix}_{date_str}_{time_str}.wav"
        
        if group_by_month:
            target_dir = os.path.join(target_root_dir, f"{prefix}_{month_str}")
            os.makedirs(target_dir, exist_ok=True)
            new_file_path = os.path.join(target_dir, new_file_name)
        else:
            new_file_path = os.path.join(target_root_dir, new_file_name)
    else:
        new_file_name = f"{prefix}_UNKNOWN_TIMESTAMP.wav"
        new_file_path = os.path.join(target_root_dir, new_file_name)

    print(f"Renaming '{file_path}' to '{new_file_path}'")
    try:
        if move:
            shutil.move(file_path, new_file_path)
            print(f"Moved '{file_path}' to '{new_file_path}'")
        else:
            shutil.copy(file_path, new_file_path)
            print(f"Copied '{file_path}' to '{new_file_path}'")
    except Exception as e:
        print(f"Failed to rename/move '{file_path}': {e}", file=sys.stderr)

def process_directory(source_directory, target_directory, move=False, group_by_month=False):
    """Process all WAV files in the given directory and its subdirectories, and concatenate all TXT files."""
    report_file_path = os.path.join(target_directory, "report.txt")
    with open(report_file_path, 'w') as report_file:
        for root, _, files in os.walk(source_directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith('.wav'):
                    try:
                        metadata = read_wildlife_acoustics_metadata(file_path)
                        if metadata:
                            rename_wav_file(file_path, metadata, target_directory, move, group_by_month)
                    except Exception as e:
                        traceback.print_exc()
                        print(f"Failed to process '{file_path}': {e}", file=sys.stderr)
                elif file.lower().endswith('.txt'):
                    try:
                        with open(file_path, 'r') as txt_file:
                            shutil.copyfileobj(txt_file, report_file)
                        print(f"Added '{file_path}' content to report.txt")
                    except Exception as e:
                        print(f"Failed to concatenate '{file_path}' into report.txt: {e}", file=sys.stderr)
                else:
                    new_file_path = os.path.join(target_directory, file)
                    try:
                        if move:
                            shutil.move(file_path, new_file_path)
                            print(f"Moved '{file_path}' to '{new_file_path}'")
                        else:
                            shutil.copy(file_path, new_file_path)
                            print(f"Copied '{file_path}' to '{new_file_path}'")
                    except Exception as e:
                        print(f"Failed to move/copy '{file_path}': {e}", file=sys.stderr)

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print('usage: %s SOURCE_DIRECTORY TARGET_DIRECTORY [--move] [--group-by-month]' % os.path.basename(sys.argv[0]), file=sys.stderr)
        sys.exit(2)

    source_directory = sys.argv[1]
    target_directory = sys.argv[2]
    move = '--move' in sys.argv
    group_by_month = '--group-by-month' in sys.argv

    if not os.path.isdir(source_directory):
        print(f"'{source_directory}' is not a valid source directory", file=sys.stderr)
        sys.exit(2)

    if not os.path.isdir(target_directory):
        os.makedirs(target_directory)

    process_directory(source_directory, target_directory, move, group_by_month)

if __name__ == '__main__':
    main()
