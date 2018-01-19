"""Aggregates a series of classifications into an attention score.

class: label: distractiveness
c0: safe driving: 1
c1: texting - right: 10
c2: talking on the phone - right: 7
c3: texting - left: 10
c4: talking on the phone - left: 7
c5: operating the radio: 6
c6: drinking: 5
c7: reaching behind: 15
c8: hair and makeup: 8
c9: talking to passenger: 5


n - 4 contrubutes 20%
n - 3 contributes 40%
n - 2 contributes 60%
n - 1 contributes 80%
n  contributes 100%

scores are summed and divided by the count of scores and then a sigmoid
function is applied, shifted by +5

formula
n[1-4] = distractiveness * confidence of prediction
x = ((n-4*0.2)+(n-3*0.4)+(n-2*0.6)+(n-1*.08)+(n))
score = 1/(1 + e^(-x+5))

The worst possible score is 0.98, the best possible score 0.01
"""

import math


def aggregate_score(results):
    """Calculate aggregate attention score from classifications."""

    # penalty for eaach kind of distraction
    class_penalties = {0: 1,
                       1: 10,
                       2: 7,
                       3: 10,
                       4: 7,
                       5: 6,
                       6: 5,
                       7: 15,
                       8: 8,
                       9: 5}

    # weight assigned to the last 5 measurements 
    weights = {0: 1,
               1: 0.8,
               2: 0.6,
               3: 0.4,
               4: 0.2}

    def shifted_sigmoid(x):
        return (1/(1 + math.exp(-x+5)))

    x = 0
    for i in range(len(results)):
        x += class_penalties[results[i][0]] * results[i][1] * weights[i]
    x /= len(results)

    attention_score = shifted_sigmoid(x)
    return attention_score
