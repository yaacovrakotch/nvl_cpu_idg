#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u

import setenv      # must be first in the imports
from gadget.getgit import GitOperations
from gadget.disk import rmtree, mkdirs
from gadget.pylog import log  # Use VepLog for logging
from gadget.files import TempDir
from gadget.shell import IS_UNIX, SystemCall
from gadget.disk import Chdir
from datetime import datetime, timezone
import sys
import os
import json
import string


def setup_logging():
    """Configure logging to output only to the console."""
    log.stdout(string_level="INFO")  # Set up console logging with the desired log level
    log.info("Logging configured to output to console with INFO level.")


def get_repo_sha_id(data):
    """ Get repo SHA id"""
    NVL_CPU = data.get('nvl.cpu', 'N/A')
    NVL_GCD = data.get('nvl.gcd', 'N/A')
    NVL_HUB = data.get('nvl.hub', 'N/A')
    NVL_PCD = data.get('nvl.pcd', 'N/A')
    NVL_COMMON = data.get('nvl.common', 'N/A')
    repo_sha_id = {'nvl-cpu': NVL_CPU, 'nvl-gcd': NVL_GCD, 'nvl-hub': NVL_HUB, 'nvl-pcd': NVL_PCD, 'nvl-common': NVL_COMMON}
    return repo_sha_id


def setting_Tags(cur_TP, repo_name, SHA, PKG):
    """
    Setting tag for 5 repos.
    """
    log.info("Setup ENV proxy")
    os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'
    log.info(f'Set tag for : {repo_name}')
    with TempDir(name=True) as repos_path:
        repo_url = f"https://github.com/intel-restricted/{repo_name.replace('-', '.')}.git"
        GitOperations.clone_repository(repo_url, repos_path)
        log.info(f'Current directory: {repos_path}')
        GitOperations.update_submodule(repos_path, '.')
        GitOperations.checkout_branch(repos_path, SHA)
        # get dielet name and bom name
        reposhort = repo_name.split('-')[-1]
        dielet = reposhort[0].upper()
        # convert date to tagname ##add by CS
        current = datetime.now(timezone.utc)
        print(f"Current Time is {current}")
        year, week, weekday = current.isocalendar()
        suffix = 'A'
        base_workweek = f"{str(year)[-1]}{week}{weekday}"
        workweek = base_workweek + suffix
        print(workweek)

        existing_tags = GitOperations.get_all_tags(repos_path)
        # Checking if current TAG exists
        # cur_tag = f'{cur_TP}_{workweek}_{PKG}'  # add by CS
        for suffix in string.ascii_uppercase:
            workweek = base_workweek + suffix
            cur_tag = f'{cur_TP}_{workweek}_{dielet}{PKG}'
            if cur_tag in existing_tags:
                log.info(f'{cur_tag} exists.')
            if cur_tag not in existing_tags:
                log.info(f'new tag is {cur_tag}.')
                break

        # Adding a tag on the current SHA
        log.info(f'Adding new tag CMD: git tag {cur_tag} {SHA}')
        GitOperations.create_tag(repos_path, cur_tag, SHA)
        GitOperations.push_tag(repos_path, cur_tag)
        log.info(f'Tag {cur_tag} pushed successfully.')
        return cur_tag


def setting_CommonTags(cur_tag, repo_name, SHA):
    log.info("Setup ENV proxy")
    os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'
    log.info(f'Set tag for : {repo_name}')
    with TempDir(name=True) as repos_path:
        repo_url = f"https://github.com/intel-restricted/{repo_name.replace('-', '.')}.git"
        GitOperations.clone_repository(repo_url, repos_path)
        log.info(f'Current directory: {repos_path}')
        GitOperations.update_submodule(repos_path, '.')
        GitOperations.checkout_branch(repos_path, SHA)
        for tag in cur_tag:
            # Adding a tag on the current SHA
            log.info(f'Adding new tag CMD: git tag {tag} {SHA}')
            GitOperations.create_tag(repos_path, tag, SHA)
            GitOperations.push_tag(repos_path, tag)
        log.info(f'Tag {cur_tag} pushed successfully.')
        return cur_tag


class GoldFailTag:

    def main(self):
        """Main entry point for creating pull requests."""
        setup_logging()
        Gold = os.environ.get('GoldDielet', '').strip()
        Fail = os.environ.get('FailDielet', '').strip()
        # Gold = "CPU,PCD" ## for Debug
        # Fail = "" ## for Debug
        TP_path = os.environ.get('TPPath', '').strip()
        GoldItems = [item.strip().lower() for item in Gold.split(",") if item.strip()]
        FailItems = [item.strip().lower() for item in Fail.split(",") if item.strip()]
        GoldItems.append("common")
        # TP_path = f'I:\\engineering\\dev\\team_classtp\\torch\\GoldFailTag\\DRV_2\\POR_TP\\Class_NVL_S52C' ## for Debug
        # TP_path = f'I:\\engineering\\dev\\team_client_tpi\\chungshe\\TestProgram\\DRV_2\\POR_TP\\Class_NVL_S52C' ## for Debug
        # Dielets = os.environ.get('Dielet', '').strip() ## for Debug
        # Flags = os.environ.get('Flag', '').strip() ## for Debug
        last_part = TP_path.split('\\')[-1]       # 'Class_NVL_S52C'
        # Check if it's an NVL product
        if 'NVL' in last_part:
            # For NVL products, only take the last part
            Bom = last_part.split('_')[-1]        # 'S52C'
        else:
            # For non-NVL products, take first letter + last part
            parts = last_part.split('_')
            first_letter = parts[1][0]              # First letter of product (DNL->D, RZL->R)
            last_part_bom = parts[-1]               # Last part (S28C, S52C)
            Bom = f"{first_letter}{last_part_bom}"  # DS28C, RS52C
        print(f"PKG is {Bom}")

        # Getting repo sha id
        repo_sha = f"{TP_path}/Reports/RepoRev.json"
        with open(repo_sha, "r") as json_file:
            data = json.load(json_file)
        # Return a dict for repo_sha_id = {nvl-cpu: SHA,...}
        repo_sha_id = get_repo_sha_id(data)
        # Adding Tag to the test program:
        # Set default values
        default_ver = "1"
        default_stepping = "A"
        default_ver_path = os.path.join(TP_path, "InputFiles", "MajorRevision.txt")
        default_stepping_path = os.path.join(TP_path, "InputFiles", "DieletStepping.txt")
        # Try reading from file1.txt
        try:
            with open(default_ver_path) as f1:
                num_part = f1.read().strip()
                if not num_part:  # empty, missing, or evaluates to False...
                    num_part = default_ver
        except FileNotFoundError:
            num_part = default_ver
            print("Common Repo MajorRev file not found")
        # Try reading from file2.txt
        try:
            with open(default_stepping_path) as f2:
                letter_part = f2.read().strip().upper()
                if not letter_part:
                    letter_part = default_stepping
        except FileNotFoundError:
            letter_part = default_stepping
            print("Dielet stepping file not found")
        # Combine into final name
        short_name = f"G{num_part}{letter_part}"
        print(f"Gold Version is {short_name}")  # Example output: G1A
        forCommonTag = []
        for key, value in repo_sha_id.items():
            if value != 'N/A':
                key_suffix = key.split("-")[-1].lower()
                if key_suffix in GoldItems:
                    if key_suffix == 'common':
                        cur_tag = setting_CommonTags(forCommonTag, key, value)
                    else:
                        cur_tag = setting_Tags(short_name, key, value, Bom)
                        forCommonTag.append(cur_tag)
                else:
                    print(f" Gold Tag No match for: {key} and {GoldItems}")
        print(f'completed set Gold')
        short_name = "FAIL"
        for key, value in repo_sha_id.items():
            if value != 'N/A':
                key_suffix = key.split("-")[-1].lower()
                if key_suffix in FailItems:
                    cur_tag = setting_Tags(short_name, key, value, Bom)
                else:
                    print(f" Fail Tag No match for: {key} and {FailItems}")
        print(f'completed set Fail')


if __name__ == "__main__":
    gold_fail_tag = GoldFailTag()
    gold_fail_tag.main()
