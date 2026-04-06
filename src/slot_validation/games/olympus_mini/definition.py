from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OlympusMiniDefinition:
    """
    Fixed game definition for Olympus Mini.

    This file contains game invariants:
    - board shape
    - fixed state names
    - fixed trigger semantics
    - fixed round resolution semantics
    - fixed multiplier accumulation semantics

    These are NOT external config parameters.
    """

    game_id: str = "olympus_mini"

    # Board shape
    board_rows: int = 5
    board_cols: int = 6

    # Fixed state names
    base_state_name: str = "basic"
    free_state_name: str = "free"

    # Scatter trigger semantics
    base_free_trigger_count: int = 4
    retrigger_count: int = 3

    # Fixed free spin awards
    base_awarded_free_spins: int = 15
    retrigger_awarded_free_spins: int = 5

    # Round semantics
    multiplier_applies_to_entire_round_win: bool = True
    multiplier_applies_after_cascade_chain_ends: bool = True

    # Base-game multiplier semantics
    base_round_multiplier_resets_after_round: bool = True

    # Free-game multiplier semantics
    free_game_has_global_multiplier: bool = True
    free_game_global_multiplier_starts_at_zero: bool = True
    free_game_collects_round_multiplier_into_global: bool = True
    free_game_global_multiplier_accumulates_by_addition: bool = True

    # Application condition for free-game global multiplier:
    # in free game, previously collected global multiplier only participates
    # when the current winning round also contains multiplier symbol(s)
    free_game_global_multiplier_applies_only_if_current_round_has_multiplier_symbol: bool = True

    # If a free-game winning round has multiplier symbols,
    # final applied multiplier = current_round_multiplier + stored_global_multiplier
    free_game_applied_multiplier_combines_current_and_global_by_addition: bool = True

    # Symbol behavior semantics
    regular_symbols_can_form_wins: bool = True
    scatter_symbols_do_not_pay_as_regular_cluster: bool = True
    multiplier_symbols_do_not_pay_as_regular_cluster: bool = True

    scatter_participates_in_cascade_clear: bool = False
    multiplier_participates_in_cascade_clear: bool = False

    # Strip / multiplier profile lock scope
    strip_set_selection_scope: str = "round"
    multiplier_profile_selection_scope: str = "round"

    # Refill semantics
    refill_reuses_same_round_strip_set: bool = True
    refill_reuses_same_round_multiplier_profile: bool = True


OLYMPUS_MINI_DEFINITION = OlympusMiniDefinition()


ROUND_RESOLUTION_ORDER: tuple[str, ...] = (
    "evaluate_regular_symbol_wins",
    "clear_winning_regular_symbols",
    "refill_empty_positions",
    "repeat_until_no_regular_win",
    "collect_round_multiplier_from_visible_multiplier_symbols",
    "apply_round_multiplier_to_round_win",
    "check_scatter_trigger",
    "pay_scatter",
    "enter_free_game_if_triggered",
)