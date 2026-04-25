def win_x(win_amount: float, bet_amount: float) -> float:
    if bet_amount <= 0:
        return 0.0
    return win_amount / bet_amount


def final_free_carry(bet) -> float:
    carry = 0.0
    for rnd in bet.rounds:
        if rnd.round_type == "free" and rnd.base_symbol_win_amount > 0.0:
            carry = rnd.carried_multiplier + rnd.round_multiplier_increment
    return carry


def fmt_float(value: float) -> str:
    return f"{value:.6f}"
