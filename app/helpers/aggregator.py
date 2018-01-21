"""Aggregates a classification and the previous score into an updated score.

class: label: distractiveness
c0: safe driving: 1
c1: texting - right: 7
c2: talking on the phone - right: 6
c3: texting - left: 7
c4: talking on the phone - left: 6
c5: operating the radio: 5
c6: drinking: 4
c7: reaching behind: 10
c8: hair and makeup: 7
c9: talking to passenger: 3


current score is the class penalty multiplied by  confidence
previous score is added, and sum is divided by 2
"""


def aggregate_score(prev_score, curr_label, curr_confidence):
    """Calculate aggregate attention score from classifications."""

    # penalty for eaach kind of distraction
    class_penalties = {0: 1,
                       1: 7,
                       2: 6,
                       3: 7,
                       4: 6,
                       5: 5,
                       6: 4,
                       7: 10,
                       8: 7,
                       9: 3}

    current_score = class_penalties[curr_label] * curr_confidence
    aggregate_score = (current_score + prev_score) / 2

    return aggregate_score
