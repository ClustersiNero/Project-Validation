from configs.game import olympus_mini
from validation.api import run
from validation.core.types import MetricRule, PipelineResult, ValidationRules


def _pipeline_config() -> dict:
    return {
        "seed": 42,
        "mode_id": 1,
        "bet_count": 1,
        "simulation_mode": olympus_mini.SIMULATION_MODE,
        "paytable": olympus_mini.PAYTABLE,
        "multiplier_data": olympus_mini.MULTIPLIER_DATA,
        "strip_sets": olympus_mini.STRIP_SETS,
        "implementation_config": olympus_mini.IMPLEMENTATION_CONFIG,
    }


def test_pipeline_smoke():
    result = run(_pipeline_config())

    assert isinstance(result, PipelineResult)

    # canonical structure
    metadata = result.canonical_result.simulation_metadata
    assert metadata.simulation_id == "simulation-seed-42"
    assert metadata.config_id == "simulation_config"
    assert metadata.config_version == "0.1.0"
    assert metadata.engine_version == "engine.v1"
    assert metadata.schema_version == "canonical.v1"
    assert metadata.mode == "normal"
    assert metadata.seed == 42
    assert metadata.bet_amount == 1.0
    assert metadata.bet_level == 1.0
    assert metadata.total_bets == 1
    assert metadata.timestamp == "1970-01-01T00:00:00Z"

    assert len(result.canonical_result.bets) == 1
    assert len(result.canonical_result.bets[0].rounds) == 1
    assert len(result.canonical_result.bets[0].rounds[0].rolls) == 1

    # round ids
    assert result.canonical_result.bets[0].rounds[0].round_id == 0

    # canonical internal consistency
    bet = result.canonical_result.bets[0]
    assert bet.round_count == 1
    assert bet.bet_win_amount == sum(rnd.round_win_amount for rnd in bet.rounds)
    assert bet.basic_win_amount == sum(rnd.round_win_amount for rnd in bet.rounds if rnd.round_type == "basic")
    assert bet.free_win_amount == sum(rnd.round_win_amount for rnd in bet.rounds if rnd.round_type == "free")
    assert bet.bet_win_amount == bet.basic_win_amount + bet.free_win_amount
    for rnd in bet.rounds:
        assert rnd.base_symbol_win_amount == sum(r.roll_win_amount for r in rnd.rolls)
        assert rnd.carried_multiplier == 0.0
        assert rnd.round_total_multiplier == 1.0
        assert rnd.award_free_rounds == 0
        assert rnd.scatter_win_amount == 0.0
        assert rnd.round_win_amount == sum(r.roll_win_amount for r in rnd.rolls)
        assert rnd.round_win_amount == rnd.base_symbol_win_amount * rnd.round_total_multiplier + rnd.scatter_win_amount
        assert rnd.rolls[0].roll_type == "initial"
        assert rnd.rolls[0].strip_set_id in {1, 2}
        for roll in rnd.rolls:
            assert roll.strip_set_id == rnd.rolls[0].strip_set_id
            assert roll.multiplier_profile_id in olympus_mini.MULTIPLIER_DATA["weight"]
            assert len(roll.roll_filled_state) == 5
            assert all(len(row) == 6 for row in roll.roll_filled_state)
            for row in roll.roll_filled_state:
                for cell in row:
                    assert cell.symbol_id in olympus_mini.PAYTABLE
                    if olympus_mini.PAYTABLE[cell.symbol_id]["symbol_type"] == "multiplier":
                        assert cell.multiplier_value is not None
                    else:
                        assert cell.multiplier_value is None
            assert len(roll.roll_final_state) == 5
            assert all(len(row) == 6 for row in roll.roll_final_state)
            for row in roll.roll_final_state:
                for cell in row:
                    if cell is None:
                        continue
                    assert cell.symbol_id in olympus_mini.PAYTABLE
                    if olympus_mini.PAYTABLE[cell.symbol_id]["symbol_type"] == "multiplier":
                        assert cell.multiplier_value is not None
                    else:
                        assert cell.multiplier_value is None
            assert rnd.round_final_state == rnd.rolls[-1].roll_final_state
            assert bet.bet_final_state == bet.rounds[-1].round_final_state

    # metrics counts
    assert result.metrics_bundle.meta.total_bets == 1
    assert result.metrics_bundle.round_metrics.core.round_count == 1
    assert result.metrics_bundle.roll_metrics.core.roll_count == 1

    # metrics totals consistent with canonical
    assert result.metrics_bundle.meta.total_bet_win_amount == bet.bet_win_amount
    assert result.metrics_bundle.round_metrics.core.total_round_win_amount == sum(
        rnd.round_win_amount for rnd in bet.rounds
    )
    assert result.metrics_bundle.roll_metrics.core.total_roll_win_amount == sum(
        r.roll_win_amount for rnd in bet.rounds for r in rnd.rolls
    )
    assert result.metrics_bundle.bet_metrics.core.avg_bet_win_amount.observed == bet.bet_win_amount
    assert result.metrics_bundle.round_metrics.core.avg_round_win_amount.observed == sum(
        rnd.round_win_amount for rnd in bet.rounds
    )
    assert result.metrics_bundle.roll_metrics.core.avg_roll_win_amount.observed == sum(
        r.roll_win_amount for rnd in bet.rounds for r in rnd.rolls
    )

    # validation
    assert result.canonical_validation.is_valid is True
    assert result.canonical_validation.issues == []
    assert result.metrics_validation.is_valid is True
    assert result.metrics_validation.issues == []
    assert result.statistical_validation is None


def test_pipeline_can_run_statistical_validation_when_rules_are_supplied():
    rules = ValidationRules(
        metrics={
            "MetricsBundle.bet_metrics.core.empirical_rtp": MetricRule(
                expected_range=(0.0, 1000.0),
            )
        }
    )

    result = run(_pipeline_config(), validation_rules=rules)

    assert result.statistical_validation is not None
    assert result.statistical_validation.is_valid is True
    assert len(result.statistical_validation.statistical_checks) == 1
    check = result.statistical_validation.statistical_checks[0]
    assert check.metric_path == "MetricsBundle.bet_metrics.core.empirical_rtp"
    assert check.check_type == "range"
    assert check.verdict == "pass"
