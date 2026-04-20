from configs.game import olympus_mini
from validation.config.simulation_config import normalize_simulation_config, load_simulation_config


def test_seed_preserved_through_normalize():
    raw = {
        "seed": 99,
    }
    config = normalize_simulation_config(raw)
    assert config.seed == 99


def test_seed_default_when_absent():
    raw = {}
    config = normalize_simulation_config(raw)
    assert config.seed == 0


def test_mode_id_default_when_absent():
    raw = {}
    config = normalize_simulation_config(raw)
    assert config.mode_id == 1


def test_bet_count_default_when_absent():
    raw = {}
    config = normalize_simulation_config(raw)
    assert config.bet_count == 1


def test_seed_preserved_through_load():
    raw = {
        "seed": 7,
    }
    config = load_simulation_config(raw)
    assert config.seed == 7


def test_module_load_carries_implementation_config():
    config = load_simulation_config(olympus_mini)

    assert config.mode_id == 1
    assert config.bet_count == 1
    assert config.implementation_config is olympus_mini.IMPLEMENTATION_CONFIG
