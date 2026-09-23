"""
This basically builds the delivery report and saves it as JSON.

Here Efficiency is calculated as the average distance travelled per package:
Efficiency = total_distance / packages_delivered.

Agents with no deliveries have an efficiency of 0.0 and are not considered
when selecting the best agent.
"""
import json
import csv
from typing import Dict, Optional
from models import Agent


def build_report(agents: Dict[str, Agent]) -> dict:
    report = {}
    best_agent_id: Optional[str] = None
    best_efficiency = float("inf")

    for agent_id in sorted(agents.keys()):
        agent = agents[agent_id]

        if agent.packages_delivered > 0:
            efficiency = round(agent.total_distance / agent.packages_delivered, 2)
        else:
            efficiency = 0.0

        report[agent_id] = {
            "packages_delivered": agent.packages_delivered,
            "total_distance": round(agent.total_distance, 2),
            "efficiency": efficiency,
        }

        if agent.packages_delivered > 0 and efficiency < best_efficiency:
            best_efficiency = efficiency
            best_agent_id = agent_id

    report["best_agent"] = best_agent_id
    return report


def save_report(report: dict, filepath: str = "report.json") -> None:
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)



# This is a Bonus task : export just the best agent's stats to a CSV file.
def export_top_performer_csv(report: dict, filepath: str = "top_performer.csv") -> None:
    
    best = report.get("best_agent")
    if best is None:
        return # Nothing to export if no agent delivered a package.
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["agent_id", "packages_delivered", "total_distance", "efficiency"])
        writer.writerow([
            best,
            report[best]["packages_delivered"],
            report[best]["total_distance"],
            report[best]["efficiency"],
        ])
