#!/usr/bin/python
"""
Recursively read all WAV files in a directory, extract WAMD metadata, 
and rename the files based on the metadata.

usage::

    $> rename_wav_files.py SOURCE_DIRECTORY TARGET_DIRECTORY [--move]
"""

import os
import sys
import shutil
import traceback
from read_wa_metadata import read_wildlife_acoustics_metadata

def rename_wav_file(file_path, metadata, target_root_dir, move=False):
    """Rename and move/copy the WAV file based on its metadata."""
    prefix = metadata.get('prefix', 'UNKNOWN')
    timestamp = metadata.get('timestamp')
    if timestamp:
        date_str = timestamp.strftime('%Y%m%d')
        time_str = timestamp.strftime('%H%M%S')
        new_file_name = f"{prefix}_{date_str}_{time_str}.wav"
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

def process_directory(source_directory, target_directory, move=False):
    """Process all WAV files in the given directory and its subdirectories."""
    for root, _, files in os.walk(source_directory):
        for file in files:
            if file.lower().endswith('.wav'):
                file_path = os.path.join(root, file)
                try:
                    metadata = read_wildlife_acoustics_metadata(file_path)
                    if metadata:
                        rename_wav_file(file_path, metadata, target_directory, move)
                except Exception as e:
                    traceback.print_exc()
                    print(f"Failed to process '{file_path}': {e}", file=sys.stderr)

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print('usage: %s SOURCE_DIRECTORY TARGET_DIRECTORY [--move]' % os.path.basename(sys.argv[0]), file=sys.stderr)
        sys.exit(2)

    source_directory = sys.argv[1]
    target_directory = sys.argv[2]
    move = len(sys.argv) == 4 and sys.argv[3] == '--move'

    if not os.path.isdir(source_directory):
        print(f"'{source_directory}' is not a valid source directory", file=sys.stderr)
        sys.exit(2)

    if not os.path.isdir(target_directory):
        print(f"'{target_directory}' is not a valid target directory", file=sys.stderr)
        sys.exit(2)

    process_directory(source_directory, target_directory, move)

if __name__ == '__main__':
    main()
