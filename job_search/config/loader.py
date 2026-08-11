import os
import yaml
from pathlib import Path


DEFAULT_CONFIG_PATH = Path(__file__).parent / "candidate_profile.yaml"


def load_config(config_path=None):
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_candidate_info(config=None):
    if config is None:
        config = load_config()
    return config.get("candidate", {})


def get_target_roles(config=None):
    if config is None:
        config = load_config()
    roles = config.get("target_roles", {})
    tier1 = roles.get("tier1", [])
    tier2 = roles.get("tier2", [])
    return {"tier1": tier1, "tier2": tier2, "all": tier1 + tier2}


def get_reject_roles(config=None):
    if config is None:
        config = load_config()
    return config.get("reject_roles", [])


def get_locations(config=None):
    if config is None:
        config = load_config()
    return config.get("locations", {})


def get_search_config(config=None):
    if config is None:
        config = load_config()
    return config.get("search", {})


def get_scoring_weights(config=None):
    if config is None:
        config = load_config()
    return config.get("scoring_weights", {})


def get_experience_filter(config=None):
    if config is None:
        config = load_config()
    return config.get("experience_filter", {})


def get_mode(config=None):
    if config is None:
        config = load_config()
    return config.get("mode", "discovery")
