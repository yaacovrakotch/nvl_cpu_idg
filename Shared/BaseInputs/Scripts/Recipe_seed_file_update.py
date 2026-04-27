"""
Using Python 3.12 rev and above for the script

Recipe seed file + config file update might cause old golden sha/tag/branch not backward compatible.
This script will update the recipe seeds directory path to old rev globally including all BOMs.

Type of Usage:
    Run the script in test program folder level where Base Test Plan file exists.
    Input the seed directory path to be updated.
    Example: I:/engineering/dev/sctp/recipe_gen/hdmx/nvl/seed/R07_NVL
    Confirm all .tpconfig files are updated with the new seed directory path for all BOMs.
"""
import os
import fnmatch
import re

def find_tpconfig_files(root='.'):
    # Find all .tpconfig files matching the pattern path/POR_TP/Class_*/Class_*.tpconfig
    matches = []
    for dirpath, dirnames, filenames in os.walk(root):
        norm_path = os.path.normpath(dirpath)
        if norm_path.split(os.sep)[0] == 'Shared':
            continue
        parts = norm_path.split(os.sep)
        # Check if parent directory also starts with Class_
        if len(parts) >= 2 and parts[-2] == 'POR_TP' and parts[-1].startswith('Class_'):
            for filename in filenames:
                if fnmatch.fnmatch(filename, 'Class_*.tpconfig'):
                    matches.append(os.path.join(dirpath, filename))
    return matches

def update_seeds_directory(file_path, new_directory):
    # Parse the file content
    with open(file_path, 'rb') as f:
        content = f.read()
    line_ending = b'\r\n' if b'\r\n' in content else b'\n'
    lines = content.split(line_ending)
    pattern = re.compile(rb'^\s*<Seeds\s+DirectoryName="[^"]*"')
    updated = False
    # Update matching lines
    for i, line in enumerate(lines):
        if pattern.match(line):
            # Use a lambda to safely insert the new directory name
            new_line = re.sub(
                rb'DirectoryName="[^"]*"',
                lambda m: b'DirectoryName="' + new_directory.encode('utf-8') + b'"',
                line
            )
            lines[i] = new_line
            updated = True
            break
    if updated:
        with open(file_path, 'wb') as f:
            f.write(line_ending.join(lines))
    return updated

if __name__ == '__main__':
    new_dir = input('Enter User Target Seeds DirectoryName value: ').strip()
    files = find_tpconfig_files()
    for f in files:
        if update_seeds_directory(f, new_dir):
            print(f'Updated: {f}')
