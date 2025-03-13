def prob_A_win(eloA: float, eloB:float )-> float:
    return 1 / (1 + 10**((eloB - eloA) / 400))

def get_new_rating(eloA: float, eloB: float, result: bool, k=32) -> float:
    return eloA + k * (result - prob_A_win(eloA, eloB))