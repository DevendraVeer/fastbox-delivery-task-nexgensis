"""
This file loads and parses the input JSON file.

The input files use two different formats for warehouses and agents,
so the loader supports both and converts them into the same format.

Style A (test_case_1.json):

    "warehouses": {"W1": [x, y], "W2": [x, y], ...}
    "agents": {"A1": [x, y], ...}
    "packages": [{"id": "P1", "warehouse": "W1", "destination": [x, y]}, ...]

Style B (base_case.json):

    "warehouses": [{"id": "W1", "location": [x, y]}, ...]
    "agents": [{"id": "A1", "location": [x, y]}, ...]
    "packages": [{"id": "P1", "warehouse_id": "W1", "destination": [x, y]}, ...]
"""

import json
from typing import Dict, Tuple
from models import Warehouse, Agent, Package


def _normalize_location_block(block, field_name: str) -> Dict[str, Tuple[float, float]]:
    """
    Normalizes either:
        {"W1": [x, y], "W2": [x, y]}                   -> dict style (Style A)
    or
        [{"id": "W1", "location": [x, y]}, ...]         -> list style (Style B)
    into a plain dict: {"W1": (x, y), ...}
    """
    normalized = {}

    if isinstance(block, dict):
        for entity_id, coords in block.items():
            normalized[entity_id] = (float(coords[0]), float(coords[1]))

    elif isinstance(block, list):
        for entry in block:
            entity_id = entry["id"]
            coords = entry["location"]
            normalized[entity_id] = (float(coords[0]), float(coords[1]))

    else:
        raise ValueError(f"Unrecognized JSON structure for '{field_name}': {type(block)}")

    if not normalized:
        raise ValueError(f"'{field_name}' is empty — need at least one entry")

    return normalized


def load_data(filepath: str): #This loads the JSON file and creates Warehouse, Agent, and Package objects.
    
    
    
    with open(filepath, "r") as f:
        raw = json.load(f)

    for required_key in ("warehouses", "agents", "packages"):
        if required_key not in raw:
            raise KeyError(f"Input JSON is missing required top-level key: '{required_key}'")

    warehouse_coords = _normalize_location_block(raw["warehouses"], "warehouses")
    agent_coords = _normalize_location_block(raw["agents"], "agents")

    warehouses = {wid: Warehouse(id=wid, location=loc) for wid, loc in warehouse_coords.items()}
    agents = {aid: Agent(id=aid, location=loc, start_location=loc) for aid, loc in agent_coords.items()}

    packages: Dict[str, Package] = {}
    for pkg in raw["packages"]:
        # Support both input formats
        wh_id = pkg.get("warehouse", pkg.get("warehouse_id"))
        if wh_id is None:
            raise KeyError(f"Package '{pkg.get('id')}' has neither 'warehouse' nor 'warehouse_id' field")
        if wh_id not in warehouses:
            raise ValueError(f"Package '{pkg.get('id')}' references unknown warehouse '{wh_id}'")

        packages[pkg["id"]] = Package(
            id=pkg["id"],
            warehouse_id=wh_id,
            destination=(float(pkg["destination"][0]), float(pkg["destination"][1])),
        )

    return warehouses, agents, packages
