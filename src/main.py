"""
This file runs the FastBox delivery simulation.

Flow of project:
    load data -> assign packages -> simulate deliveries -> build report

Usage:
    python main.py <input.json> [options]
"""


import argparse
import copy
import sys

from data_loader import load_data
from assignment import assign_packages
from simulator import simulate_deliveries
from report import build_report, save_report, export_top_performer_csv
from visualizer import render_ascii_map
from bonus_features import add_agent_mid_day


def run_pipeline(input_path: str, output_path: str, simulate_delays: bool, seed: int):
    warehouses, agents, packages = load_data(input_path)

    assign_packages(agents, warehouses, packages)
    simulate_deliveries(agents, warehouses, packages, simulate_delays=simulate_delays, seed=seed)

    report = build_report(agents)
    save_report(report, output_path)

# Check that all packages were delivered.
    total_delivered = sum(a.packages_delivered for a in agents.values())
    if total_delivered != len(packages):
        print(
            f"WARNING: {total_delivered} delivered but {len(packages)} packages exist. "
            f"This should never happen -- please report as a bug.",
            file=sys.stderr,
        )

    return warehouses, agents, packages, report


def main():
    parser = argparse.ArgumentParser(description="FastBox Mystery Delivery System simulator")
    parser.add_argument("input_json", help="Path to the input JSON file")
    parser.add_argument("--output", default="report.json", help="Where to save the report (default: report.json)")
    parser.add_argument("--no-delays", action="store_true", help="Disable the random-delay bonus feature")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for delays (default: 42)")
    parser.add_argument("--csv", action="store_true", help="Also export the top performer to CSV")
    parser.add_argument("--ascii", action="store_true", help="Print an ASCII map of the final layout")
    parser.add_argument("--demo-new-agent", action="store_true",
                         help="Demonstrate the mid-day new-agent bonus feature on a COPY of the data")
    args = parser.parse_args()

    warehouses, agents, packages, report = run_pipeline(
        args.input_json, args.output, simulate_delays=not args.no_delays, seed=args.seed
    )

    print("\n=== DELIVERY REPORT ===")
    for agent_id, stats in report.items():
        if agent_id == "best_agent":
            continue
        print(f"  {agent_id}: delivered={stats['packages_delivered']:<3} "
              f"distance={stats['total_distance']:<8} efficiency={stats['efficiency']}")
    print(f"  Best agent: {report['best_agent']}")
    print(f"\nSaved report to: {args.output}")

    if args.csv:
        csv_path = args.output.rsplit(".", 1)[0] + "_top_performer.csv"
        export_top_performer_csv(report, csv_path)
        print(f"Saved top performer CSV to: {csv_path}")

    if args.ascii:
        print("\n=== ASCII MAP (final agent positions) ===")
        print(render_ascii_map(warehouses, agents))

    if args.demo_new_agent:
        print("\n=== BONUS DEMO: new agent joining mid-day ===")
# Load fresh data for the demo so the main report stays unchanged.
        wh2, ag2, pk2 = load_data(args.input_json)
        assign_packages(ag2, wh2, pk2)
# Deliver the first half of each agent's packages.
        for agent in ag2.values():
            half = len(agent.assigned_packages) // 2
# Leave the remaining packages for the re-assignment step.
            agent.assigned_packages = agent.assigned_packages[:half]
        simulate_deliveries(ag2, wh2, pk2, simulate_delays=not args.no_delays, seed=args.seed)

        new_id = "A_NEW"
        new_location = (50, 50)
        add_agent_mid_day(ag2, wh2, pk2, new_id, new_location, seed=args.seed)

        demo_report = build_report(ag2)
        print(f"New agent '{new_id}' joined at {new_location}.")
        for agent_id, stats in demo_report.items():
            if agent_id == "best_agent":
                continue
            print(f"  {agent_id}: delivered={stats['packages_delivered']:<3} "
                  f"distance={stats['total_distance']:<8} efficiency={stats['efficiency']}")
        print(f"  Best agent (after new agent joined): {demo_report['best_agent']}")


if __name__ == "__main__":
    main()
