import pandas

# Three CSV files describing a 5/2021 Israeli opinion poll.
codes_for_questions = pandas.read_csv("./codes_for_questions.csv")
codes_for_answers = pandas.read_csv("./codes_for_answers.csv")
list_of_answers = pandas.read_csv("./list_of_answers.csv")


def _party_from_label(labels: pandas.Series) -> pandas.Series:
    # Labels look like "מחל - הליכוד בהנהגת בנימין נתניהו לראשות הממשלה". The party code is the part before
    # the first " - ". n=1 splits only once, so "ר - רפא - רק בריאות בראשות דוקטור אריה אבני" -> "ר".
    return labels.str.split(" - ", n=1).str[0]  # take the text before the first " - "


def _q2_code(party: str) -> int:
    # Find the numeric Q2 code (1..17) that represents the given party.
    q2_rows = codes_for_answers[codes_for_answers["Value"] == "Q2"] # keep only Q2 answer options
    match = q2_rows[_party_from_label(q2_rows["Label"]) == party] # row whose party code matches
    return int(match["Code"].iloc[0]) # return that row's numeric code


def _q3_column(party: str) -> str:
    # Find the Q3_x column name that belongs to the given party.
    q3_rows = codes_for_questions[codes_for_questions["Variable"].str.startswith("Q3_", na=False)] # only Q3_x rows
    match = q3_rows[_party_from_label(q3_rows["Label"]) == party] # row whose party code matches
    return str(match["Variable"].iloc[0]) # return the column name (e.g. "Q3_1")


def support_in_one_party_elections(party: str) -> int:
    """
    Number of respondents who chose `party` in the single-vote system (Q2).

    >>> support_in_one_party_elections("מחל")
    134
    >>> support_in_one_party_elections("פה")
    109
    >>> support_in_one_party_elections("ר")
    3
    >>> support_in_one_party_elections("עם")
    21
    """
    code = _q2_code(party) # party letters -> Q2 numeric code
    return int((list_of_answers["Q2"] == code).sum()) # count rows whose Q2 equals that code


def support_in_multi_party_elections(party: str) -> int:
    """
    Number of respondents who approved `party` in the multi-vote system (Q3).

    >>> support_in_multi_party_elections("מחל")
    162
    >>> support_in_multi_party_elections("פה")
    131
    >>> support_in_multi_party_elections("ר")
    13
    >>> support_in_multi_party_elections("עם")
    27
    """
    column = _q3_column(party) # party letters -> "Q3_x" column name
    return int(list_of_answers[column].sum()) # Yes=1, No=0, so the sum is the Yes count


def parties_with_different_relative_order() -> tuple:
    """
    Return a pair (A, B) of parties whose ranking is flipped between the two
    systems: A beats B in Q2 but B beats A in Q3. Return None if no such pair
    exists.

    On this dataset such a flip DOES exist: ('אמת', 'כן').
        אמת -> Q2 = 34, Q3 = 85
        כן  -> Q2 = 33, Q3 = 93
    אמת leads in the single-vote system (34 > 33) but כן overtakes it in the
    multi-vote system (93 > 85), so the relative order between them flips.

    The doctest below also checks (independently) that the returned pair is
    really a flip, by recomputing both counts with the other two functions.

    The doctest checks four things:
      (1) the function returns a pair (not None),
      (2) the pair contains two different parties,
      (3) in the single-vote system (Q2) party A beats party B,
      (4) in the multi-vote system  (Q3) party B beats party A -- the flip.

    >>> result = parties_with_different_relative_order()
    >>> result is None # (1) a flipped pair was found
    False
    >>> isinstance(result, tuple) and len(result) == 2
    True
    >>> a, b = result # unpack the pair into A and B
    >>> a != b # (2) A and B are different parties
    True
    >>> a_q2 = support_in_one_party_elections(a) # single-vote count for A
    >>> b_q2 = support_in_one_party_elections(b) # single-vote count for B
    >>> a_q2 > b_q2 # (3) A leads B in the single-vote system
    True
    >>> a_q3 = support_in_multi_party_elections(a) # multi-vote count for A
    >>> b_q3 = support_in_multi_party_elections(b) # multi-vote count for B
    >>> b_q3 > a_q3 # (4) B leads A in the multi-vote system -> ORDER FLIPPED
    True
    """
    # Q2 count per party.
    q2 = codes_for_answers[codes_for_answers["Value"] == "Q2"].copy() # rows describing Q2 options
    q2["party"] = _party_from_label(q2["Label"]) # extract party code from label
    q2["q2"] = q2["Code"].map(list_of_answers["Q2"].value_counts()).fillna(0).astype(int) # Q2 vote count per party

    # Q3 count per party (sum each Q3_x column).
    q3_sums = list_of_answers.filter(like="Q3_").sum().astype(int) # Q3 column -> Yes count
    q3 = codes_for_questions[codes_for_questions["Variable"].str.startswith("Q3_", na=False)].copy() # rows for Q3_x columns
    q3["party"] = _party_from_label(q3["Label"]) # extract party code from label
    q3["q3"] = q3["Variable"].map(q3_sums).astype(int) # Q3 approval count per party

    # Cross-join all (A, B) pairs, keep the first flip: A>B in Q2 but A<B in Q3.
    parties = q2[["party", "q2"]].merge(q3[["party", "q3"]], on="party") # one row per party, both counts
    pairs = parties.merge(parties, how="cross", suffixes=("_a", "_b")) # every ordered pair (A, B)
    flips = pairs[(pairs["q2_a"] > pairs["q2_b"]) & (pairs["q3_a"] < pairs["q3_b"])] # keep only flipped pairs
    if flips.empty:  # no flip exists in the data
        return None

    row = flips.iloc[0] # first flipped pair we found
    return row["party_a"], row["party_b"]


if __name__ == '__main__':
    import doctest
    print(doctest.testmod())

    # Use this code for testing via console input-output:
    # party = input()
    # if party == "parties_with_different_relative_order":
    #     print(parties_with_different_relative_order())
    # else:
    #     print(support_in_one_party_elections(party), support_in_multi_party_elections(party))