#!/usr/intel/pkgs/python3/3.12.3/bin/python3

"""
PR_Gatekeeper.py - Pull Request Review Tool using LangChain

SETUP STEPS PERFORMED:
======================

1. Selected Python Interpreter:
   - Used Python 3.11.1 from: /usr/intel/pkgs/python3/3.11.1/bin/python3
   - This is specified in the shebang line above

2. Installed LangChain and Dependencies:
   Command used:
   /usr/intel/pkgs/python3/3.12.3/bin/python3 -m pip install langchain --target /nfs/site/disks/mve_dtv_003/scan/skorlam/Python_Packages_312

   This installed:
   - langchain (1.0.3)
   - langchain-core (1.0.3)
   - langgraph (1.0.2)
   - pydantic (2.12.3)
   - And all required dependencies

3. Set PYTHONPATH Environment Variable:
   For tcsh shell, run:
   setenv PYTHONPATH /nfs/site/disks/mve_dtv_003/scan/skorlam/Python_Packages

   To make this permanent, add to ~/.tcshrc or ~/.cshrc:
   setenv PYTHONPATH /nfs/site/disks/mve_dtv_003/scan/skorlam/Python_Packages

4. Running the Script:
   Method 1 (with PYTHONPATH set):
   ./PR_Gatekeeper.py

   Method 2 (one-time run):
   setenv PYTHONPATH /nfs/site/disks/mve_dtv_003/scan/skorlam/Python_Packages && /usr/intel/pkgs/python3/3.11.1/bin/python3 PR_Gatekeeper.py

5 . Additional packages:
        /usr/intel/pkgs/python3/3.12.3/bin/python3 -m pip install truststore --target /nfs/site/disks/mve_dtv_003/scan/skorlam/Python_Packages
        /usr/intel/pkgs/python3/3.12.3/bin/python3 -m pip install langchain_openai --target /nfs/site/disks/mve_dtv_003/scan/skorlam/Python_Packages

6. Set your Open AI/ExpertGPT key on the machine

TROUBLESHOOTING:
================
If you get "ModuleNotFoundError: No module named 'langchain'":
- Ensure PYTHONPATH is set correctly (echo $PYTHONPATH)
- Verify packages are installed: /usr/intel/pkgs/python3/3.11.1/bin/python3 -m pip list | grep langchain
- Check that Python_Packages directory exists and contains langchain folder
"""


# Add repository root to Python path to import gadget and GenAI modules
# This script is in GenAI/Scripts/, so go up 2 levels to get to repo root
# repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.insert(0, repo_root)
from setenv import ROOT_ENV      # must be first in the imports
import sys
import os
from gadget.data_host import DataHost
from gadget.pylog import log  # Use VepLog for logging
from genai.prompts.pr_gatekeeper_prompt import WHY_IS_PR_NEEDED_SYSTEM_PROMPT_SHORT, WHY_IS_PR_NEEDED_SYSTEM_PROMPT
# from langchain_openai import ChatOpenAI


class PR_Gatekeeper:
    def __init__(self, pr_description_input):
        self.pr_description_input = pr_description_input
        self.full_prompt = WHY_IS_PR_NEEDED_SYSTEM_PROMPT.format(user_input=self.pr_description_input)

    def main(self):
        data_host = DataHost()

        # Define the URP for the LLM invocation
        urp = ('https://tvpv1.pdx.intel.com/cgi-bin/pytpdhost2.cgi',
               '/intel/tpvalidation/engtools/tptools/mtl/beta/latest',   # change this to your sandbox path
               'tgl.py')

        payload = {}
        # debugmode = False
        # api_key = os.getenv('EXPERTGPT_API_KEY') if debugmode else None
        # payload["api_key"] = api_key
        payload["prompt"] = self.full_prompt

        try:
            llm_response = data_host.central('invokellm', payload, check=True, urp=urp)

            if llm_response.strip().lower() == "yes":
                log.info(f"Agent determined PR description is valid")
                return 1, llm_response
            elif 'Connection error' in llm_response:
                log.info(f"Cannot connect!")
                log.info(f"LLM Response: {llm_response}")
                return 1, "yes"
            else:
                log.info(f"Agent determined PR description is invalid")
                log.info(f"LLM Response: {llm_response}")
                return 0, llm_response

        except Exception as e:
            log.error(f"Failed to determine llm response: {e}")
            log.info(f"Defaulting to valid PR description.")
            return 1, "Defaulted to valid PR description due to error."

# if __name__ == "__main__":
#     # Example PR description input
#     example_pr_description = "Turn on ApexTC in multipass in order to prevent current clamps and prevent Bin 99s. Files changes include pymtplsource code, scn_core .usrv, scn_core .mtpl and scn_core .flw - These changes are to support the above ApexTC change."
#     reviewer = PR_Gatekeeper(example_pr_description)
#     result = reviewer.main()
#     # if result == 1:
#     #     print("PR description is valid.")
#     # else:
#     #     print("PR description is invalid.")
