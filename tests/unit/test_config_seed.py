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


def test_seed_preserved_through_load():
    raw = {
        "seed": 7,
        "rounds": [
            {"round_id": 0, "round_type": "basic", "roll_wins": [0.5]},
        ],
    }
    config = load_minimal_config(raw)
    assert config.seed == 7
