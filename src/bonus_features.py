"""
This is also basically a bonus feature.
It handles adding a new agent during the simulation (mid-day basically).
Undelivered packages are reassigned to the nearest available agent,
while already delivered packages are left unchanged.
"""

from typing import Dict
from models import Agent, Warehouse, Package
from distance import euclidean_distance
from simulator import simulate_deliveries


def add_agent_mid_day(agents: Dict[str, Agent], warehouses: Dict[str, Warehouse],
                       packages: Dict[str, Package], new_agent_id: str,
                       new_agent_location, seed: int = 42) -> None:

# This adds a new agent and reassigns the remaining packages.

    # 1. Bring the new agent onto the field.
    agents[new_agent_id] = Agent(
        id=new_agent_id,
        location=tuple(new_agent_location),
        start_location=tuple(new_agent_location),
    )

# Collect packages that still need to be delivered.
    undelivered_ids = [pid for pid, pkg in packages.items() if not pkg.delivered]
    for agent in agents.values():
        agent.assigned_packages = [pid for pid in agent.assigned_packages if pid not in undelivered_ids]

    for package_id in sorted(undelivered_ids):
        package = packages[package_id]
        warehouse = warehouses[package.warehouse_id]

        best_agent_id, best_distance = None, float("inf")
        for agent_id in sorted(agents.keys()):
            agent = agents[agent_id]
# Use the current position for agents already on a route.

            reference_point = agent.location if agent.packages_delivered > 0 else agent.start_location
            dist = euclidean_distance(reference_point, warehouse.location)
            if dist < best_distance:
                best_distance = dist
                best_agent_id = agent_id

        agents[best_agent_id].assigned_packages.append(package_id)

# Continue the simulation with the updated assignments..
    simulate_deliveries(agents, warehouses, packages, simulate_delays=True, seed=seed)
