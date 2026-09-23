"""
This basically simulates package deliveries and tracks the distance travelled by each agent.
Packages are handled using a nearest-warehouse approach. Agents continue
from their current position, so the simulation can be run more than once.
"""

import random
from typing import Dict, Optional
from models import Agent, Warehouse, Package
from distance import euclidean_distance

DELAY_PROBABILITY = 0.15   # 15% chance a given delivery leg is delayed
DELAY_RANGE_MINUTES = (1, 10)


def simulate_deliveries(agents: Dict[str, Agent], warehouses: Dict[str, Warehouse],
                         packages: Dict[str, Package], simulate_delays: bool = True,
                         seed: Optional[int] = 42) -> None:

# This simulates deliveries and updates the agents and packages in place.

    rng = random.Random(seed)

    for agent_id in sorted(agents.keys()):  # deterministic processing order
        agent = agents[agent_id]

 # Skip packages that have already been delivered.

        remaining = [pid for pid in agent.assigned_packages if not packages[pid].delivered]     
 # Continue from the agent's current position.

        current_pos = agent.location if agent.packages_delivered > 0 else agent.start_location

        while remaining:
 # Pick the closest remaining warehouse.

            nearest_pkg_id = min(
                remaining,
                key=lambda pid: euclidean_distance(current_pos, warehouses[packages[pid].warehouse_id].location)
            )
            package = packages[nearest_pkg_id]
            warehouse = warehouses[package.warehouse_id]

            leg_to_warehouse = euclidean_distance(current_pos, warehouse.location)
            leg_to_destination = euclidean_distance(warehouse.location, package.destination)

            agent.total_distance += leg_to_warehouse + leg_to_destination
            agent.route_log.append(
                f"{agent.id}: move -> {package.warehouse_id} (+{leg_to_warehouse:.2f}) "
                f"-> pickup {package.id} -> deliver @ {tuple(round(c, 1) for c in package.destination)} "
                f"(+{leg_to_destination:.2f})"
            )

            if simulate_delays and rng.random() < DELAY_PROBABILITY:
                package.delay = round(rng.uniform(*DELAY_RANGE_MINUTES), 2)

            package.delivered = True
            agent.packages_delivered += 1
            current_pos = package.destination
            remaining.remove(nearest_pkg_id)

        agent.location = current_pos  # Save the agent's final position.

