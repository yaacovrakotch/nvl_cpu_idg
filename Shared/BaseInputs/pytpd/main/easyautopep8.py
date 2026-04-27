#!/usr/intel/pkgs/python3/3.6.3a/modules/r1/bin/python3 -u

# this script is a wrapper script for main/autopep8.py
# we want to call with the following arguments, ex
# main/autopep8.py <files_to_fix> -i -r --ignore=E402,E501,W503,W504,W605,E712 -aaa -p 50
# files_to_fix is a list of files to fix, passed as arguments to this script
import sys
import subprocess
import os


def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to autopep8.py in the same directory
    autopep8_path = os.path.join(script_dir, 'autopep8.py')

    # Check if autopep8.py exists
    if not os.path.exists(autopep8_path):
        print(f"Error: autopep8.py not found at {autopep8_path}")
        sys.exit(1)

    # Get files to fix from command line arguments
    files_to_fix = sys.argv[1:]

    if not files_to_fix:
        print("Usage: easyautopep8.py <file1> [file2] [file3] ...")
        print("Example: easyautopep8.py pymtpl/binctr.py pymtpl/core.py")
        sys.exit(1)

    # Build the command with all required arguments
    cmd = [
        sys.executable,  # Use the current Python interpreter
        autopep8_path
    ] + files_to_fix + [
        '-i',
        '-r',
        '--ignore=E402,E501,W503,W504,W605,E712',
        '-aaa',
        '-p', '50'
    ]

    print(f"Running: {' '.join(cmd)}")

    # Execute the command
    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Error running autopep8: {e}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':  # pragma: no cover
    main()
