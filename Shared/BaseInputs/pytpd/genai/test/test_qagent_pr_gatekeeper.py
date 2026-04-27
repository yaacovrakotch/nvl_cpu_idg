#!/usr/intel/pkgs/python3/3.12.3/bin/python3
"""
unittest for PR_Gatekeeper
"""
from setenv_unittest import ROOT_ENV     # must be first import for unittests

from gadget.ut import TestCase, unittest, MockVar, is_ut_option
from gadget.data_host import DataHost
from unittest.mock import Mock, patch
from collections import defaultdict
from gadget.gizmo import Elapsed
from genai.qagent_pr_gatekeeper import PR_Gatekeeper
from genai.prompts.pr_gatekeeper_prompt import WHY_IS_PR_NEEDED_SYSTEM_PROMPT_SHORT, WHY_IS_PR_NEEDED_SYSTEM_PROMPT
import os


class TestPRReviewer(TestCase):
    """Unittest for PR_Gatekeeper"""

    def test_init_basic(self):
        # Test PR_Gatekeeper initialization with basic input
        pr_desc = "Adding feature X to improve performance"
        reviewer = PR_Gatekeeper(pr_desc)

        self.assertEqual(reviewer.pr_description_input, pr_desc)
        self.assertIn(pr_desc, reviewer.full_prompt)
        self.assertIsNotNone(reviewer.full_prompt)

    def test_init_empty_input(self):
        # Test PR_Gatekeeper initialization with empty input
        reviewer = PR_Gatekeeper("")

        self.assertEqual(reviewer.pr_description_input, "")
        self.assertIn("", reviewer.full_prompt)

    def test_prompt_formatting(self):
        # Test that the full prompt is correctly formatted with user input
        test_input = "This is a test PR description"
        reviewer = PR_Gatekeeper(test_input)

        # Verify the prompt contains the user input
        self.assertIn(test_input, reviewer.full_prompt)

        # Verify the prompt structure matches the expected format
        expected_prompt = WHY_IS_PR_NEEDED_SYSTEM_PROMPT.format(user_input=test_input)
        self.assertEqual(reviewer.full_prompt, expected_prompt)

    def test_main_valid_response_yes(self):
        # Test main() with valid LLM response 'yes'
        reviewer = PR_Gatekeeper("Valid PR description explaining why this change is needed")

        # Mock the DataHost central method to return 'yes'
        def mock_central(self, command, data, check=True, **kwargs):
            return "yes"

        with patch.object(DataHost, 'central', mock_central):
            result, response = reviewer.main()
            self.assertEqual(result, 1)

    def test_main_valid_response_connection(self):
        reviewer = PR_Gatekeeper("Valid PR description explaining why this change is needed")

        # Mock the DataHost central method to return 'yes'
        def mock_central(self, command, data, check=True, **kwargs):
            return 'Error invoking LLM model: Connection error'

        with patch.object(DataHost, 'central', mock_central):
            result, response = reviewer.main()
            self.assertEqual(result, 1)

    def test_main_valid_response_Yes_case_insensitive(self):
        # Test main() with valid LLM response 'Yes' (case insensitive)
        reviewer = PR_Gatekeeper("Valid PR description")

        def mock_central(self, command, data, check=True, **kwargs):
            return "Yes"

        with patch.object(DataHost, 'central', mock_central):
            result, response = reviewer.main()
            self.assertEqual(result, 1)

    def test_main_invalid_response_no(self):
        # Test main() with invalid LLM response 'no'
        reviewer = PR_Gatekeeper("Just adding feature")

        def mock_central(self, command, data, check=True, **kwargs):
            return "no"

        with patch.object(DataHost, 'central', mock_central):
            result, response = reviewer.main()
            self.assertEqual(result, 0)

    def test_main_invalid_response_No_case_insensitive(self):
        # Test main() with invalid LLM response 'No' (case insensitive)
        reviewer = PR_Gatekeeper("Vague description")

        def mock_central(self, command, data, check=True, **kwargs):
            return "No"

        with patch.object(DataHost, 'central', mock_central):
            result, response = reviewer.main()
            self.assertEqual(result, 0)

    def test_main_unclear_response_defaults_valid(self):
        # Test main() with unclear LLM response defaults to valid
        reviewer = PR_Gatekeeper("Some PR description")

        def mock_central(self, command, data, check=True, **kwargs):
            return "maybe"

        with patch.object(DataHost, 'central', mock_central):
            result, response = reviewer.main()
            self.assertEqual(result, 0)

    def test_main_empty_response_defaults_valid(self):
        # Test main() with empty LLM response defaults to valid
        reviewer = PR_Gatekeeper("Some PR description")

        def mock_central(self, command, data, check=True, **kwargs):
            return "yes"

        with patch.object(DataHost, 'central', mock_central):
            result, response = reviewer.main()
            self.assertEqual(result, 1)

    def test_main_response_with_whitespace(self):
        # Test main() handles responses with leading/trailing whitespace
        reviewer = PR_Gatekeeper("Valid PR description")

        # Test with whitespace around 'yes'
        def mock_central_yes(self, command, data, check=True, **kwargs):
            return "  YES  "

        with patch.object(DataHost, 'central', mock_central_yes):
            result, response = reviewer.main()
            self.assertEqual(result, 1)

        # Test with whitespace around 'no'
        def mock_central_no(self, command, data, check=True, **kwargs):
            return "  no  "

        with patch.object(DataHost, 'central', mock_central_no):
            result, response = reviewer.main()
            self.assertEqual(result, 0)

    def test_main_exception_handling(self):
        # Test main() handles exceptions from DataHost
        reviewer = PR_Gatekeeper("Test PR description")

        def mock_central_exception(self, command, data, check=True, **kwargs):
            raise Exception("Connection error")

        with patch.object(DataHost, 'central', mock_central_exception):
            result, response = reviewer.main()
            # Should return 1 (valid) when exception occurs - defaults to permissive
            self.assertEqual(result, 1)

    def test_main_calls_correct_datahost_method(self):
        # Test that main() calls DataHost.central with correct parameters
        reviewer = PR_Gatekeeper("Test description")

        called_args = []

        def mock_central(self, command, data, check=True, **kwargs):
            called_args.append({'command': command, 'data': data, 'check': check, 'kwargs': kwargs})
            return "yes"

        with patch.object(DataHost, 'central', mock_central):
            reviewer.main()

            # Verify correct parameters were passed
            self.assertEqual(len(called_args), 1)
            self.assertEqual(called_args[0]['command'], 'invokellm')
            self.assertEqual(called_args[0]['check'], True)
            self.assertIn("Test description", called_args[0]['data']['prompt'])

    def test_special_characters_in_input(self):
        # Test PR_Gatekeeper handles special characters in input
        special_input = "PR with special chars: \n\t<>&\"'"
        reviewer = PR_Gatekeeper(special_input)

        self.assertEqual(reviewer.pr_description_input, special_input)
        self.assertIn(special_input, reviewer.full_prompt)

    def test_long_input(self):
        # Test PR_Gatekeeper handles long input strings
        long_input = "This is a very long PR description. " * 100
        reviewer = PR_Gatekeeper(long_input)

        self.assertEqual(reviewer.pr_description_input, long_input)
        self.assertIn(long_input, reviewer.full_prompt)

    def test_unicode_input(self):
        # Test PR_Gatekeeper handles unicode characters
        unicode_input = "PR description with unicode: 你好 🎉 café"
        reviewer = PR_Gatekeeper(unicode_input)

        self.assertEqual(reviewer.pr_description_input, unicode_input)
        self.assertIn(unicode_input, reviewer.full_prompt)

    def test_multiline_input(self):
        # Test PR_Gatekeeper handles multiline input
        multiline_input = """This PR is needed because:
1. It fixes a critical bug
2. It improves performance
3. It adds new features"""
        reviewer = PR_Gatekeeper(multiline_input)

        self.assertEqual(reviewer.pr_description_input, multiline_input)
        self.assertIn(multiline_input, reviewer.full_prompt)


class TestPRReviewerIntegration(TestCase):
    """Integration tests for PR_Gatekeeper (may require actual DataHost connection)"""

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="on development only", neg=False))
    def test_real_datahost_valid_description(self):
        # Test with real DataHost connection - valid description
        reviewer = PR_Gatekeeper(
            "Adding retry logic to prevent timeout failures in production environments"
        )
        # This would call the actual DataHost
        result, response = reviewer.main()
        self.assertEqual(result, 1)
        # pass  # Uncomment above when testing with real connection

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="on development only", neg=False))
    def test_real_datahost_invalid_description(self):
        # Test with real DataHost connection - invalid description
        reviewer = PR_Gatekeeper("Adding new feature")
        # This would call the actual DataHost
        # result = reviewer.main()
        # self.assertEqual(result, 0)
        pass  # Uncomment above when testing with real connection


class EvaluateGenAiBinary:

    @classmethod
    def evaluate(cls, repeat, inputs, routine):
        """
        Framework to evaluate (repeatability and accurancy) of a genai routine which has a binary output
        """
        result_set = defaultdict(set)
        for idx in range(repeat):
            for userinput, reponse in inputs.items():
                sw = Elapsed()
                result, agent_response = routine(userinput)
                # result = 1
                result_set[userinput].add(result)
                print("Run_ID:", idx, "Run_Result:", result, "Time_Elapsed:", sw, "User_Input:", userinput)

        # print the repeatability
        # repeatability is 100% (all items are repeatable). 75% repeatable if 3 of 4 items are repeatable.
        passcnt = 0
        for userinput in result_set:
            if len(result_set[userinput]) == 1:
                passcnt += 1
            else:
                print(f"Not repeatable: {userinput}: {result_set[userinput]}")

        msg_repeat = f'=> Repeatable percentage is {passcnt * 100 / len(result_set): .1f}%'

        # print the accuracy
        # accuracy is total correct response / total responses  (this includes repeat)
        totalcnt = 0
        passcnt = 0
        for userinput in result_set:
            for result in result_set[userinput]:
                totalcnt += 1
                if result == inputs[userinput]:
                    passcnt += 1
                else:
                    print(f"Incorrect result: {userinput}")

        print()
        print(msg_repeat)
        print(f'=> Accuracy percentage is {passcnt * 100 / totalcnt: .1f}%')


class Evaluate_PRGatekeeper(TestCase):
    """Perform repeatability and correctness"""
    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="on development only", neg=False))
    def evaluate_pr_gatekeeper(self):
        # TODO: use a different token for this
        def hook(userinput):
            return PR_Gatekeeper(userinput).main()

        inputs = {"Plist uprev to p5 with pattern re-order to fix the DRNG post process fail and Patmod enable with additional delays for FMIN test to pass": 1,
                  "This PR is needed to re-enable LTTC screening in the flow in order screen out any cold defects at Class hot itself": 1,
                  "Enable mts1500 hvm_timing": 0,
                  "NVLP FUN_GT plist uprev with refresh pre": 0}

        return EvaluateGenAiBinary.evaluate(5, inputs, hook)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
