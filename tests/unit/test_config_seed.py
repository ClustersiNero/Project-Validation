from validation.config.minimal_config import normalize_minimal_config, load_minimal_config


def test_seed_preserved_through_normalize():
    raw = {
        "seed": 99,
        "rounds": [
            {"round_id": 0, "round_type": "basic", "roll_wins": [1.0]},
        ],
    }
    config = normalize_minimal_config(raw)
    assert config.seed == 99


def test_seed_default_when_absent():
    raw = {
        "rounds": [
            {"round_id": 0, "round_type": "basic", "roll_wins": [1.0]},
        ],
    }
    config = normalize_minimal_config(raw)
    assert config.seed == 0
    assert config.simulation_id == "minimal-seed-0"


def test_seed_preserved_through_load():
    raw = {
        "seed": 7,
        "rounds": [
            {"round_id": 0, "round_type": "basic", "roll_wins": [0.5]},
        ],
    }
    config = load_minimal_config(raw)
    assert config.seed == 7


def test_metadata_defaults_are_deterministic():
    raw = {
        "seed": 5,
        "rounds": [
            {"round_id": 0, "round_type": "basic", "roll_wins": [1.0]},
        ],
    }

    config = normalize_minimal_config(raw)

    assert config.simulation_id == "minimal-seed-5"
    assert config.config_id == "minimal_config"
    assert config.config_version == "0.1.0"
    assert config.engine_version == "minimal_engine.v1"
    assert config.schema_version == "canonical.v1"
    assert config.mode == "normal"
    assert config.bet_amount == 1.0
    assert config.bet_level == 1.0
    assert config.timestamp == "1970-01-01T00:00:00Z"
