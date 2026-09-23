"""
This assigns each package to the nearest agent based on the warehouse location.

Basically here agents are compared using their starting positions so that assignments(delivery boy's)
don't change as the simulation runs. Agent IDs are checked in sorted
order to keep tie-breaking deterministic.
"""


from typing import Dict
from models import Agent, Warehouse, Package
from distance import euclidean_distance


def assign_packages(agents: Dict[str, Agent], warehouses: Dict[str, Warehouse],
                     packages: Dict[str, Package]) -> None:
    
# This assigns each package to an agent and updates their package list.

    for package_id in sorted(packages.keys()):
        package = packages[package_id]
        warehouse = warehouses[package.warehouse_id]

        best_agent_id = None
        best_distance = float("inf")

        for agent_id in sorted(agents.keys()):  # Sorted IDs make tie-breaking consistent
            agent = agents[agent_id]
            dist = euclidean_distance(agent.start_location, warehouse.location)
            if dist < best_distance:
                best_distance = dist
                best_agent_id = agent_id

        agents[best_agent_id].assigned_packages.append(package.id)
