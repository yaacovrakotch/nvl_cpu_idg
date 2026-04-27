"""
TPTorrent API for rulecheck and transfer operations.

"""
import setenv
from gadget.pylog import log
import sys
from urllib import request, parse, error
import json
import ssl
import os
from pprint import pformat
import time


class TPTorrentError(Exception):
    """Custom exception for TPTorrent client errors."""


def format_result_pretty(data):
    """Format API result for readable logging output."""
    if data is None:
        return "None"

    def collect_failed_rules(obj, results):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "failed_rules" and isinstance(value, list) and value:
                    results.append(value)
                collect_failed_rules(value, results)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                collect_failed_rules(item, results)

    if isinstance(data, (dict, list, tuple)):
        failed_rules_sections = []
        collect_failed_rules(data, failed_rules_sections)
        pretty_result = pformat(data, indent=2, width=120, compact=False, sort_dicts=True)
        if failed_rules_sections:
            failed_blocks = [
                f"failed_rules[{index + 1}]:\n{pformat(block, indent=2, width=120, compact=False)}"
                for index, block in enumerate(failed_rules_sections)
            ]
            return "\n".join([
                "****FAILED****",
                *failed_blocks,
                "",
                "Result:",
                pretty_result
            ])
        return pretty_result
    return str(data)


class TPTorrentConfig:
    """ Set TPTorrent API configuration and provide methods for authentication, rulecheck, and transfer operations. """

    def __init__(self):
        # Intel Proxy Configuration (for external Apigee token endpoint only)
        self.proxies = {
            "http": "http://proxy-dmz.intel.com:912",
            "https": "http://proxy-dmz.intel.com:912",
        }

        # API Configuration - Apigee Gateway
        self.api_base_url = "https://apis-dev.intel.com/tptorrentdev/v1"  # Development
        # self.api_base_url = "https://apis.intel.com/tptorrent/v1"  # Production

        # OAuth Configuration
        self.token_url = "https://apis-dev.intel.com/v1/auth/token"
        self.client_id = "ca521f6d-2943-4532-ac3b-c11ef6a67ec0"

        self.client_secret = bytes.fromhex("71686138517e654d314341737a34663545766e363747756c6f6d66616376495378306f5a2d646131").decode()
        # to get above hex string, use: secret_string.encode().hex()

        # Disable SSL verification (verify=False)
        self.context = ssl._create_unverified_context()

    def response_request(self, req):
        """Helper function to execute a request with proxy and SSL context."""
        opener = request.build_opener(
            request.ProxyHandler(self.proxies),
            request.HTTPSHandler(context=self.context)
        )
        response = opener.open(req, timeout=300)
        return response

    def http_error_handler(self, e):
        """Handle HTTP errors and print response body if available."""
        log.error(f"HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode("utf-8")
            try:
                log.error(f"Response:\n{json.dumps(json.loads(error_body), indent=2)}")
            except json.JSONDecodeError:
                log.error(f"Response: {error_body}")
        except Exception:
            pass
        raise TPTorrentError(f"HTTP Error {e.code}: {e.reason}") from e

    def get_access_token(self):
        """Get OAuth2 access token from Apigee using client credentials flow."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        # Encode form data
        encoded_data = parse.urlencode(data).encode()
        req = request.Request(
            self.token_url,
            data=encoded_data,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        # Get response
        response = self.response_request(req)
        token_data = json.loads(response.read().decode())
        return token_data["access_token"]

    def get_input_file(self, file_path):
        """Read input parameters from a tptorrent_input_file.txt file."""
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format in input file: {e}")

    def lookup_transfer_status(self, access_token, tp, destination_drive, product, destination):
        """
        Lookup the transfer status of a test program.

        :param access_token: access token obtained from get_access_token()
        :param tp: test program name
        :param destination_drive: destination drive
        :param product: product name
        :param destination: destination site
        """
        url = f"{self.api_base_url}/tptransfers"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "tp": tp,
            "destination_drive": destination_drive,
            "product": product,
            "destination": destination
        }

        print(f"Calling API: GET {url}")
        print(f"Params: {json.dumps(params, indent=2)}")
        try:
            # Build URL with query params (requests params= equivalent)
            if params:
                query_string = parse.urlencode(params)
                full_url = f"{url}?{query_string}"
            else:
                full_url = url

            req = request.Request(
                full_url,
                method="GET",
                headers=headers
            )

            # Execute request
            response = self.response_request(req)
            status_code = response.status
            response_body = response.read().decode("utf-8")

            # Equivalent to raise_for_status()
            if status_code >= 400:
                raise error.HTTPError(
                    full_url, status_code, response.reason, response.headers, None
                )

            print(f"Status Code: {status_code}")
            result = json.loads(response_body)
            print(f"Response: {json.dumps(result, indent=2)}")
            return result.get("status")

        except error.HTTPError as e:
            self.http_error_handler(e)

    def transfer_tp(self, access_token, site, socket, product, tp, source_drive, destination_drive,
                    tester_type, destination, destination_type="vc", user="api_user",
                    action_type="transfer", product_postfix="", sort_process="",
                    bypass_golden_source="0"):
        """
        transfer_tp will perform both rulecheck and transfer operations.
        :param access_token: tptorrent api access token obtained from get_access_token()
        :param site: source site
        :param socket: test program socket: sort, class
        :param product: product name, ex: nvl
        :param tp: test program name
        :param source_drive: source drive: eng, v, i
        :param destination_drive: destination drive: eng, v, i
        :param tester_type: tester type, ex: hdmx
        :param destination: destination site, ex: jf, atd
        :param destination_type: destination type, ex: vc, vf
        :param user: user idsid
        :param action_type: action type, ex: transfer
        :param product_postfix: product postfix
        :param sort_process: sort process
        :param bypass_golden_source: bypass golden source
        """

        url = f"{self.api_base_url}/tptransfers"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "site": site,
            "socket": socket,
            "product": product,
            "tp": tp,
            "source_drive": source_drive,
            "destination_drive": destination_drive,
            "tester_type": tester_type,
            "destination": destination,
            "destination_type": destination_type,
            "user": user,
            "action_type": action_type,
            "product_postfix": product_postfix,
            "sort_process": sort_process,
            "bypass_golden_source": bypass_golden_source
        }
        print(f"Calling API: POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")

        try:
            # Convert JSON payload (json=payload equivalent)
            json_data = json.dumps(payload).encode("utf-8")
            req = request.Request(
                url,
                data=json_data,
                method="POST",
                headers={
                    **headers,
                    "Content-Type": "application/json"
                }
            )
            # Execute request
            response = self.response_request(req)
            status_code = response.status
            response_body = response.read().decode("utf-8")

            # Equivalent to raise_for_status()
            if status_code >= 400:
                raise error.HTTPError(
                    url, status_code, response.reason, response.headers, None
                )
            print(f"Status Code: {status_code}")
            try:
                response_json = json.loads(response_body)
                print(f"Response:\n{json.dumps(response_json, indent=2)}")
                status = response_json.get("status", "No status field in response")
                if status == "PASS":
                    transfer_status = "inprogress"
                    while transfer_status not in ["passed", "failed"]:
                        transfer_status = self.lookup_transfer_status(
                            access_token,
                            tp,
                            destination_drive,
                            product,
                            destination
                        )
                        if transfer_status in ["passed", "failed"]:
                            print(f"Final transfer status: {transfer_status}")
                            break
                        else:
                            print(f"Current transfer status: {transfer_status}")
                            print("Transfer still in progress, waiting 30 seconds before checking again...")
                            time.sleep(30)

            except json.JSONDecodeError:
                print(f"Response:\n{response_body}")
                response_json = None

            # Return JSON or text (like requests)
            return response_json if response_json is not None else response_body

        except error.HTTPError as e:
            self.http_error_handler(e)

    def check_rule(self, access_token, site, socket, product, tp, source_drive, destination_drive,
                   tester_type, dest_str, user="api_user", destination_type="vc",
                   product_postfix="", sort_process="", regression_mode="0"):
        """
        Docstring for check_rule
        :param access_token: access token obtained from get_access_token()
        :param site: source site
        :param socket: test program socket: sort, class
        :param product: product name, ex: nvl
        :param tp: test program name
        :param source_drive: source drive: eng, v, i
        :param destination_drive: destination drive: eng, v, i
        :param tester_type: tester type, ex: hdmx
        :param dest_str: destination site, ex: jf, atd
        :param user: user idsid
        :param destination_type: destination type, ex: vc, vf
        :param product_postfix: Description
        :param sort_process: sort process
        :param regression_mode: regression mode
        """

        url = f"{self.api_base_url}/rulechecks"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "site": site,
            "socket": socket,
            "product": product,
            "tp": tp,
            "source_drive": source_drive,
            "destination_drive": destination_drive,
            "tester_type": tester_type,
            "dest_str": dest_str,
            "user": user,
            "destination_type": destination_type,
            "product_postfix": product_postfix,
            "sort_process": sort_process,
            "regression_mode": regression_mode
        }

        print(f"Calling API: POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("-" * 60)
        try:
            # Convert JSON payload (requests json=payload equivalent)
            json_data = json.dumps(payload).encode("utf-8")
            req = request.Request(
                url,
                data=json_data,
                method="POST",
                headers={
                    **headers,
                    "Content-Type": "application/json"
                }
            )
            # Execute request
            response = self.response_request(req)
            status_code = response.status
            response_body = response.read().decode("utf-8")
            print(f"Status Code: {status_code}")

            # Print rate limit headers if present
            resp_headers = response.headers
            if "TPT-RateLimit-Limit" in resp_headers:
                print(f"Rate Limit: {resp_headers.get('TPT-RateLimit-Limit')}")
                print(f"Rate Limit Remaining: {resp_headers.get('TPT-RateLimit-Remaining')}")
                print(f"Rate Limit Reset: {resp_headers.get('TPT-RateLimit-Reset')}")
                print(f"Retry After: {resp_headers.get('Retry-After')} seconds")
            print(f"Response:\n{response_body}")

            # Equivalent to raise_for_status() AFTER printing
            if status_code >= 400:
                raise error.HTTPError(
                    url, status_code, response.reason, resp_headers, None
                )
            # Try to parse JSON
            try:
                return json.loads(response_body)
            except json.JSONDecodeError:
                return response_body

        except error.HTTPError as e:
            self.http_error_handler(e)


def main():
    """
    Main entry point for TPTorrent API client. Reads input parameters from a JSON file, obtains an access token,
    and performs the requested TPTorrent operations.
    """
    log.info("Starting TPTorrent API Client...\n")
    if len(sys.argv) != 2:
        log.error("Usage: python tptorrent.py <tptorrent_input_file.json>")
        return 1

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        log.error(f"Input file not found: {input_file}")
        return 1

    # Get OAuth token first
    log.info("Obtaining OAuth access token...")
    tptorrent = TPTorrentConfig()
    try:
        token = tptorrent.get_access_token()
        log.info("Token obtained successfully\n")
    except Exception as e:
        log.error(f"Failed to get access token: {e}")
        log.error("Make sure APIGEE_CLIENT_ID and APIGEE_CLIENT_SECRET environment variables are set")
        return 1

    # Read input parameters from file
    try:
        input_data = tptorrent.get_input_file(input_file)
    except ValueError as e:
        log.error(f"Failed to read input file: {e}")
        return 1

    # Set input params
    tptorrent_rulecheck = input_data.get("tptorrent_rulecheck", "No")
    tptorrent_transfer = input_data.get("tptorrent_transfer", "No")
    transfer_site = input_data.get("transfer_site", "")
    socket = input_data.get("socket", "")
    product = input_data.get("product", "")
    tp_path = os.environ.get("DEST", "")
    if tp_path == "":
        log.info("DEST environment variable not set. the tp path will be taken from the input file.")
        tp = input_data.get("tp", "")
    else:
        log.info(f"DEST environment variable found: {tp_path}. It will override the tp value in the input file.")
        tp = os.path.basename(tp_path)
    source_drive = input_data.get("source_drive", "")
    destination_drive = input_data.get("destination_drive", "")
    tester_type = input_data.get("tester_type", "")
    destination_site = input_data.get("destination_site", "")
    destination_type = input_data.get("destination_type", "vc")
    idsid = input_data.get("idsid", "")

    fail_flag = 0
    for dest_site in destination_site.split(","):
        log.info(f"Initiating transfer to destination: {dest_site.strip()}")
        destination_site = dest_site.strip()  # Update destination_site for each transfer

        if tptorrent_transfer.lower() == "yes":
            log.info("TPTorrent transfer requested. Validating required parameters...")
            required_params = {
                "transfer_site": transfer_site,
                "socket": socket,
                "product": product,
                "tp": tp,
                "source_drive": source_drive,
                "destination_drive": destination_drive,
                "tester_type": tester_type,
                "destination_site": destination_site,
                "destination_type": destination_type,
                "idsid": idsid
            }
            missing_params = [key for key, value in required_params.items() if not value]
            if missing_params:
                log.error(f"Missing required parameters for transfer: {', '.join(missing_params)}")
                log.error("Please provide all required parameters in the input file or as environment variables.")
                return 1
            else:
                log.info("All required parameters for transfer are present.\n")

            try:
                result = tptorrent.transfer_tp(
                    access_token=token,
                    site=transfer_site,
                    socket=socket,
                    product=product,
                    tp=tp,
                    source_drive=source_drive,
                    destination_drive=destination_drive,
                    tester_type=tester_type,
                    destination=destination_site,
                    destination_type=destination_type,
                    user=idsid,
                    action_type="transfer",
                    product_postfix="",
                    sort_process="",
                    bypass_golden_source="0"
                )
            except TPTorrentError as e:
                log.error(f"Transfer failed: {e}")
                return 1

        elif tptorrent_rulecheck.lower() == "yes":
            try:
                result = tptorrent.check_rule(
                    access_token=token,
                    site=transfer_site,
                    socket=socket,
                    product=product,
                    tp=tp,
                    source_drive=source_drive,
                    destination_drive=destination_drive,
                    tester_type=tester_type,
                    dest_str=destination_site,
                    user=idsid,
                    destination_type=destination_type,  # or "vf"
                    product_postfix="",
                    sort_process="",
                    regression_mode="0"
                )
            except TPTorrentError as e:
                log.error(f"Rulecheck failed: {e}")
                return 1
        else:
            log.info("TPTorrent skipped as per input configuration.")
            result = "Rulecheck skipped."

        log.info("\n" + "=" * 60)
        log.info("Final Result:")
        log.info(f"Result:\n{format_result_pretty(result)}")

        if isinstance(result, dict) and result.get("failed_rules", []) != []:
            log.error("****FAILED RULES DETECTED IN RESULT****")
            log.error(f"FAILED RULES:\n{pformat(result['failed_rules'], indent=2, width=120, compact=False)}")
            fail_flag = 1
        log.info(f'==================== DONE TPTorrent for destination: {destination_site} ====================\n')
    return fail_flag


if __name__ == "__main__":
    sys.exit(main())
