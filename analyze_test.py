import re
import pytest
from analyze import support_in_one_party_elections, support_in_multi_party_elections, parties_with_different_relative_order
from testcases import parse_testcases

testcases = parse_testcases("testcases.txt")

def run_testcase(party:str):
    if party == "parties_with_different_relative_order":
         return f"{parties_with_different_relative_order()}"
    else:
         return f"{support_in_one_party_elections(party)} {support_in_multi_party_elections(party)}"

@pytest.mark.parametrize("testcase", testcases, ids=[testcase["name"] for testcase in testcases])
def test_cases(testcase):
    actual_output = run_testcase(testcase["input"])
    # If the expected value looks like /pattern/flags, treat it as a regex
    # (e.g. /.*/i means "any output is fine"). Otherwise compare as text.
    expected = testcase["output"]
    regex_form = re.fullmatch(r"/(.*)/([a-zA-Z]*)", expected)
    if regex_form:
        pattern, flags = regex_form.group(1), regex_form.group(2)
        re_flags = re.IGNORECASE if "i" in flags else 0
        assert re.fullmatch(pattern, actual_output, re_flags), f"Expected match for /{pattern}/{flags}, got {actual_output}"
    else:
        assert actual_output == expected, f"Expected {expected}, got {actual_output}"


def test_new_cases():

    # Q2 counts for parties not covered by the doctests / testcases.txt.
    assert support_in_one_party_elections("שס") == 13
    assert support_in_one_party_elections("כן") == 33
    assert support_in_one_party_elections("ב") == 54
    assert support_in_one_party_elections("אמת") == 34
    assert support_in_one_party_elections("מרצ") == 19
    assert support_in_one_party_elections("יז") == 3

    # Matching Q3 counts for the same extra parties.
    assert support_in_multi_party_elections("שס") == 39
    assert support_in_multi_party_elections("כן") == 93
    assert support_in_multi_party_elections("ב") == 101
    assert support_in_multi_party_elections("אמת") == 85
    assert support_in_multi_party_elections("מרצ") == 66
    assert support_in_multi_party_elections("יז") == 32

    # The flip mentioned in the docstring: אמת leads in Q2 but כן leads in Q3.
    assert support_in_one_party_elections("אמת") > support_in_one_party_elections("כן")
    assert support_in_multi_party_elections("כן") > support_in_multi_party_elections("אמת")

    # Return type must be a tuple of exactly two strings, not a list.
    result = parties_with_different_relative_order()
    assert type(result) is tuple
    assert len(result) == 2
    assert all(isinstance(name, str) for name in result)

    # Calling the function twice should give the same answer.
    assert parties_with_different_relative_order() == parties_with_different_relative_order()
