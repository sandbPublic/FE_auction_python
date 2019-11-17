from typing import List
Matrix = List[List[float]]


# Comparative Satisfaction.
# In a zero-sum game, subtract average opponent's perceived value from own.
def comp_sat(values: List[float], my_i: int) -> float:
    avg_opp_value = sum(values)
    avg_opp_value -= values[my_i]
    avg_opp_value /= (len(values) - 1)
    return values[my_i] - avg_opp_value


# Compensate for unit redundancies.
# If the worst team can complete a chapter in 3 turns,
# then no team can save more than 2 turns. Nevertheless,
# there may be three or more units that each individually
# save one turn, yet all together cannot save 3 turns.
# Together, they save less than the sum of their parts.
# the following function R satisfies:
# R(0) = 0
# R(inf) = max_v
# R(max_v/#players) = max_v/#players; no adjustment for average value
def redundancy(value: float, max_v: float, opp_ratio: float) -> float:
    try:
        return (value * max_v) / (value + max_v * opp_ratio)
    except ZeroDivisionError:
        return 0


def apply_redundancy(value_matrix: Matrix, max_values: List[float]) -> Matrix:
    opp_ratio = 1-1/len(value_matrix)
    for i in range(len(value_matrix)):
        for j in range(len(value_matrix)):
            value_matrix[i][j] = redundancy(value_matrix[i][j], max_values[i], opp_ratio)
    return value_matrix


# Finds prices that produce equalized satisfaction.
# A's satisfaction equals Handicapped Team Value - average opponent's HTV
# (from A's subjective perspective)
def pareto_prices(value_matrix: Matrix) -> List[float]:
    opp_ratio = 1-1/len(value_matrix)
    sat_values = [comp_sat(row, i) for i, row in enumerate(value_matrix)]
    return [(value - min(sat_values))*opp_ratio for value in sat_values]


# Try to maximize net satisfaction.
# However, for sufficiently similar bids,
# degenerate results may optimize naive net satisfaction.
# Add slight preference for each player considering their own team good:
# If a change would cause each player to think they would finish 8 turns sooner,
# but 1 turn later relative to average opponent, that change is neutral.
# Testing with different values shows that 1/8 has very little effect,
# values around 1 have large effect and produce close to equal team self assessment
# Seems to have low cost to satisfaction?
def allocation_score(value_matrix: Matrix, robust_factor: float) -> float:
    score = 0
    for i, row in enumerate(value_matrix):
        score += comp_sat(row, i) + row[i]*robust_factor
    return score
