#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script is run in the tp folder to process TorchDFF and update the common repository.

Needed:
    PYTPD    - https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.pytpd/pull/924
    TorchDFF - https://github.com/intel-restricted/applications.manufacturing.ate-test.torch.client.nvl.dff.nvl-dff-all/pull/340

Changes:
    - product mapping in TorchDFF yaml file, user can now add their bom freely, no pytpd dependancy
    - add new pr description format so that it is more meaningful
    - add persite releases in one yaml file, the workflow will auto select the respective site runners

Usage:
    1. goto https://github.com/intel-restricted/applications.manufacturing.ate-test.torch.client.nvl.dff.nvl-dff-all/actions/workflows/NVL_TorchDFF_Export_JF_Release.yml
    2. Submit a job
        a. select the site JF | PG | FM | IDC | BA (current runners JF & PG) (more runners to be added based on needs).
        b. add a path, some place where you want to keep the copies.
           I:\\engineering\\dev\team_classtp\\dashboard\\PG_script\\Dashboard\\JF_path\\DFF
        c. select the BOM of product to release.
        d. add your email address.
        e. if the export needs to be released, set the second argument to 'true'
           - it will help to create a new branch in the common repository
           - it will help to git add the files from latest export & processed into the common repository
           - it will create the PR in ./Modules/TPI_DFF_XXX/InputFiles/* (MTL [CLASS, RAWCLASS] & OLF)
"""
import setenv      # must be first in the imports
import glob
from gadget.pylog import log
from gadget.files import File, TempDir
from gadget.getgit import GitOperations
from gadget.shell import SystemCall
from gadget.disk import Chdir
import re
import sys
import os
import json
from os.path import basename, join
from datetime import datetime


class DffProc:
    def __init__(self):
        # Load product mapping from environment variable
        self.product_mapping = self.load_product_mapping()

    def load_product_mapping(self):
        """Load product mapping from environment variable.

        :return: Product mapping loaded from the ``PRODUCT_MAPPING`` environment variable.
        :rtype: dict
        :raises SystemExit: If the ``PRODUCT_MAPPING`` environment variable is not set or
            contains invalid JSON.
        """
        mapping_json = os.getenv('PRODUCT_MAPPING')
        if not mapping_json:
            log.error("PRODUCT_MAPPING environment variable is not set")
            sys.exit(1)

        try:
            return json.loads(mapping_json)
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse PRODUCT_MAPPING from environment: {e}")
            sys.exit(1)

    def clone_common_repository(self, common_repo_url, common_clone_dir):
        """Clone the common repository."""
        try:
            # Clone common repository
            GitOperations.clone_repository(common_repo_url, common_clone_dir)
            log.info(f"Cloned common repository to {common_clone_dir}")
        except Exception as e:
            log.error(f"Failed to clone common repository: {e}")

    def run_torch_commands(self, repo_path, output_dir, product_selection):
        torch_exe_path = "I:\\tpapps\\TORCH\\Prod22\\CLI\\Torch.exe"
        errors = []

        # Find all product folders
        all_product_folders = [f.path for f in os.scandir(join(repo_path, "MyDffMgmt")) if f.is_dir() and "Product_" in f.name]

        # Determine which product folders to process
        if product_selection == "ALL":
            product_folders = all_product_folders
        else:
            selected_products = product_selection.split(',')
            product_folders = []

            # Use product mapping for folder name resolution with exact matching
            for prod in selected_products:
                prod = prod.strip()  # Remove any whitespace
                if prod in self.product_mapping:
                    expected_folder_name = self.product_mapping[prod]
                    log.info(f"Looking for exact match: '{expected_folder_name}' for product '{prod}'")

                    # Find exact matches by comparing the folder basename
                    found = False
                    for folder_path in all_product_folders:
                        folder_name = os.path.basename(folder_path)
                        if folder_name == expected_folder_name:
                            product_folders.append(folder_path)
                            log.info(f"Found exact match: '{folder_name}' for product '{prod}'")
                            found = True
                            break

                    if not found:
                        log.warning(f"No folder found for product '{prod}' (expected: '{expected_folder_name}')")
                else:
                    log.error(f"Unknown product selection: '{prod}'. Available products: {list(self.product_mapping.keys())}")

        if not product_folders:
            log.error(f"No product folders found for selection: {product_selection}")
            log.info(f"Available product mappings: {self.product_mapping}")
            log.info("Available folders:")
            for folder in all_product_folders:
                log.info(f"  - {os.path.basename(folder)}")
            return []

        log.info("Selected product folders:")
        for folder in product_folders:
            log.info(f"  - {os.path.basename(folder)}")

        # Find the solution file
        solution_file = next(glob.iglob(join(repo_path, "*.sln")), None)
        if not solution_file:
            log.error(f"No solution file found in {repo_path}")
            return []

        log.info(f"Found solution file: {solution_file}")

        # Find the project file
        project_file = next(glob.iglob(join(repo_path, "MyDffMgmt", "*.dffproj")), None)
        if not project_file:
            log.error(f"No project file found in {repo_path}\\MyDffMgmt")
            return []

        log.info(f"Found project file: {project_file}")

        processed_files = []

        # Iterate over each product folder and run commands for both -t Class and -t OLF
        for product_folder in product_folders:
            product_name = os.path.basename(product_folder)
            types = ["Class", "OLF"]

            for type_ in types:
                command = [
                    torch_exe_path, "publish-mtl", "-t", type_,
                    "--product", product_name, "-s", solution_file,
                    "-p", project_file, "-d", output_dir
                ]
                log.info(f"Running command: {' '.join(command)}")
                try:
                    ecode, output = SystemCall(command, disp=True).run_outtxt()
                    if ecode != 0:
                        errors.append(f"Command failed for {product_name} with type {type_}: {output}")
                    else:
                        # Assuming the output contains the generated file path
                        generated_file = f"{output_dir}\\{product_name}_{type_}.xml"
                        processed_files.append(generated_file)
                except Exception as e:
                    errors.append(f"Command execution error for {product_name} with type {type_}: {e}")

        if errors:
            log.error("Errors encountered during processing:")
            for error in errors:
                log.error(error)

        return processed_files

    def cl2rc(self, input_dir):
        """
        Read MTL_ALL_*_CLASS.xml, rename by removing spaces in the name, replace file data (from OLBCC2 to OLBCC), save
        Creates MTL_ALL_*_RAWCLASS.xml files inside TPI_DFF_XXX/InputFiles based from MTL_ALL_*_CLASS.xml
        Process the latest created XML files: rename, modify content, and move them to a new directory.
        :param input_dir: Directory to search for XML files
        :return: None
        """
        # Find all XML files in the input directory
        xml_files = glob.glob(join(input_dir, '*.xml'))

        # Sort files by creation time, newest first
        xml_files.sort(key=os.path.getctime, reverse=True)

        # Process only the latest files (assuming you want to process all files created in the latest batch)
        latest_files = xml_files[:6]  # Adjust the number based on how many files you expect in the latest batch

        renamed_files = []

        # Rename files
        for f in latest_files:
            base_name, ext = os.path.splitext(basename(f))
            parts = base_name.split('_')

            # Take everything after the third underscore (index 3 and beyond)
            if len(parts) > 3:
                suffix_parts = parts[3:]  # Everything from index 3 onwards
                suffix = '_'.join(suffix_parts)  # Join them back with underscores
                new_name = f"NVL_{suffix.upper()}{ext.lower()}"
            else:
                # Fallback if there are less than 4 parts
                new_name = f"NVL_{'_'.join(parts).upper()}{ext.lower()}"

            new_path = join(os.path.dirname(f), new_name)

            # Rename the file using os.rename
            os.rename(f, new_path)
            log.info(f"Renamed {f} to {new_path}")
            renamed_files.append(new_path)

        # Process renamed files
        # Replace OLBCC2 with OLBCC
        cc2 = '<name>OLBCC2</name>'
        cc = '<name>OLBCC</name>'
        for f in renamed_files:
            with open(f, 'r') as file:
                log.info(f'-i- Reading inputFile {f}...')
                xmldata = file.read()
            xmldata = xmldata.replace(cc2, cc)
            File(f).rewrite(xmldata, 'OLBCC2 replace')

        # Replace OLBPC2 with OLBPC
        cc2 = '<name>OLBPC2</name>'
        cc = '<name>OLBPC</name>'
        for f in renamed_files:
            with open(f, 'r') as file:
                log.info(f'-i- Reading inputFile {f}...')
                xmldata = file.read()
            xmldata = xmldata.replace(cc2, cc)
            File(f).rewrite(xmldata, 'OLBPC2 replace')

        # Create the _RAWCLASS.xml files
        cl = '<first_socket_upload>PBIC_DAB'
        rc = '<first_socket_upload>RC_S1'
        raw_class_files = []
        for f in renamed_files:
            if '_CLASS.xml' in f:
                raw_class_path = f.replace('_CLASS.xml', '_RAWCLASS.xml')
                with open(f, 'r') as file:
                    log.info(f'-i- Reading inputFile {f}...')
                    xmldata = file.readlines()

                # Additional step: Replace "Class" with "RawClass" in lines containing <MTL_Name>
                xmldata = [
                    line.replace("Class", "RawClass") if "<MTL_Name>" in line else line
                    for line in xmldata
                ]

                # Join the lines back into a single string
                xmldata = ''.join(xmldata)

                # Replace first_socket_upload
                xmldata = xmldata.replace(cl, rc)

                File(raw_class_path).rewrite(xmldata, f'{raw_class_path} created')
                raw_class_files.append(raw_class_path)

        # Combine renamed files and raw class files for moving
        all_files_to_move = renamed_files + raw_class_files

        # Move processed files to a new directory
        new_dir_path = self.move_xml_files(input_dir, all_files_to_move)
        return new_dir_path

    def move_xml_files(self, input_dir, files_to_move):
        """
        Move specified XML files to a new directory named with the current date and an alphabetical suffix.
        :param input_dir: Directory to search for XML files
        :param files_to_move: List of files to move
        :return: Path to the new directory
        """
        # Get current date in YYMMDD format
        current_date = datetime.now().strftime('%y%m%d')

        # Determine the suffix by checking existing directories
        suffix = 'A'
        while True:
            new_dir_name = f"{current_date}_{suffix}"
            new_dir_path = join(input_dir, new_dir_name)
            if not os.path.exists(new_dir_path):
                os.makedirs(new_dir_path)
                break
            suffix = chr(ord(suffix) + 1)  # Increment suffix to next letter

        # Move each specified XML file to the new directory
        for xml_file in files_to_move:
            new_file_path = join(new_dir_path, basename(xml_file))
            log.info(f'Moving {xml_file} to {new_file_path}')
            os.rename(xml_file, new_file_path)

        return new_dir_path  # Return the path to the new directory

    def update_created_by(self, directory, user_email):
        """
        Update the <Created_By> tag in XML files with the user-provided email.
        :param directory: Directory containing XML files
        :param user_email: Email to replace in the <Created_By> tag
        :return: None
        """
        xml_files = glob.glob(join(directory, '*.xml'))
        for xml_file in xml_files:
            with open(xml_file, 'r') as file:
                log.info(f'-i- Reading inputFile {xml_file}...')
                xmldata = file.read()

            # Replace <Created_By> tag
            xmldata = re.sub(r'<Created_By>.*?</Created_By>', f'<Created_By>{user_email}</Created_By>', xmldata)

            File(xml_file).rewrite(xmldata, 'Updated <Created_By> tag')

    def find_available_branch_name(self, common_clone_dir):
        """
        Generate a unique branch name using timestamp.
        Format: NVLDFF/MTL_FilesUpdate_YYMMDD_HHMMSS
        """
        timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
        branch_name = f"NVLDFF/MTL_FilesUpdate_{timestamp}"

        log.info(f"Generated branch name: {branch_name}")
        return branch_name

    def update_git_repo(self, new_dir_path, common_clone_dir, user_email, selected_products=None):
        # Generate unique branch name with timestamp
        branch_name = self.find_available_branch_name(common_clone_dir)

        # Create product prefix for commit message and PR title
        product_prefix = ""
        if selected_products:
            if selected_products == "ALL":
                product_prefix = "[ALL] "
            else:
                products = selected_products.split(',')
                product_prefix = f"[{','.join(products)}] "

        try:
            with Chdir(common_clone_dir):
                # Create a new branch in the common repository
                GitOperations.create_branch(common_clone_dir, branch_name)

                # Copy processed files to the target directory in the common repository
                target_dir = join(common_clone_dir, "Modules/TPI/TPI_DFF_XXX/InputFiles/")
                os.makedirs(target_dir, exist_ok=True)
                for file in glob.glob(join(new_dir_path, '*.xml')):
                    File(file).copy(target_dir)

                # Commit changes
                commit_message = f"{product_prefix}This is an update on MTL/OLF files aligning with latest DFF/FFR releases to fix compatibility issues - {user_email} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                GitOperations.commit_changes(common_clone_dir, target_dir, commit_message)

                # Push the branch
                GitOperations.push_branch(common_clone_dir, branch_name)

                # Create a pull request
                github_token = os.getenv('DFFTOK')
                pr_title = f"{product_prefix}Automated Update of MTL Files - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                base_branch = "main"
                GitOperations.create_pull_request(
                    repo_name="intel-restricted/nvl.common",
                    branch_name=branch_name,
                    pr_title=pr_title,
                    base_branch=base_branch,
                    github_token=github_token,
                    local_path=common_clone_dir,
                    commit_message=commit_message
                )
                log.info(f"Successfully created PR for branch {branch_name}")
        except Exception as e:
            log.error(f"Failed to update Git repository: {e}")


def main():
    if len(sys.argv) < 4:
        print("Usage: python nvl_torchdff_release.py <input_directory> <product_selection> <user_email> [enable_release]")
        sys.exit(1)

    input_dir = sys.argv[1]
    product_selection = sys.argv[2]
    user_email = sys.argv[3]
    enable_release = sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else False

    # Assume the TorchDFF repository is already checked out in the current directory
    torch_repo_path = os.getcwd()  # Use the current working directory for TorchDFF repo
    common_repo_url = "https://github.com/intel-restricted/nvl.common.git"

    with TempDir(name=True) as common_clone_dir:
        obj = DffProc()
        obj.clone_common_repository(common_repo_url, common_clone_dir)
        processed_files = obj.run_torch_commands(repo_path=torch_repo_path, output_dir=input_dir, product_selection=product_selection)
        new_dir_path = obj.cl2rc(input_dir)  # Process and rename files

        # Update <Created_By> tag with user email
        obj.update_created_by(new_dir_path, user_email)

        if enable_release:
            obj.update_git_repo(new_dir_path, common_clone_dir, user_email, product_selection)


if __name__ == '__main__':  # pragma: no cover
    main()
