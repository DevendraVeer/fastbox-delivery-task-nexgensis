"""

Bonus task : This visualize routes in ASCII.

Coordinates are scaled to fit the grid. Warehouses are shown as W and
agents are shown using the number from their ID.

"""

from typing import Dict
from models import Warehouse, Agent


def render_ascii_map(warehouses: Dict[str, Warehouse], agents: Dict[str, Agent],
                      width: int = 60, height: int = 22) -> str:
    all_x = [w.location[0] for w in warehouses.values()] + [a.location[0] for a in agents.values()]
    all_y = [w.location[1] for w in warehouses.values()] + [a.location[1] for a in agents.values()]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    x_range = (max_x - min_x) or 1  
    y_range = (max_y - min_y) or 1

    grid = [[" " for _ in range(width)] for _ in range(height)]

    def place(x, y, char):
        col = int((x - min_x) / x_range * (width - 1))
        row = int((max_y - y) / y_range * (height - 1))  # flip y axis
        grid[row][col] = char

    for wh in warehouses.values():
        place(wh.location[0], wh.location[1], "W")

    for agent_id in sorted(agents.keys()):
        agent = agents[agent_id]
        # Use the agent ID number as the marker
        marker = "".join(ch for ch in agent_id if ch.isdigit()) or "A"
        place(agent.location[0], agent.location[1], marker[-1])

    border = "+" + "-" * width + "+"
    lines = [border] + ["|" + "".join(row) + "|" for row in grid] + [border]
    legend = "Legend: W = warehouse | digit = agent's final position (e.g. '1' = A1)"
    return "\n".join(lines) + "\n" + legend
