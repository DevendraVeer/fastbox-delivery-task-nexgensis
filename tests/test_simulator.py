"""
Tests for the FastBox delivery pipeline.

Run with:
    python -m pytest tests/
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_loader import load_data
from assignment import assign_packages
from simulator import simulate_deliveries
from report import build_report

TEST_CASES_DIR = os.path.join(os.path.dirname(__file__), "..", "test_cases")
ALL_INPUT_FILES = sorted(
    f for f in os.listdir(TEST_CASES_DIR)
    if f.startswith(("test_case_", "base_case")) and f.endswith(".json") and "example_output" not in f
)


class TestFastBoxPipeline(unittest.TestCase):

    def _run(self, filename):
        path = os.path.join(TEST_CASES_DIR, filename)
        warehouses, agents, packages = load_data(path)
        assign_packages(agents, warehouses, packages)
        simulate_deliveries(agents, warehouses, packages, simulate_delays=False)
        report = build_report(agents)
        return warehouses, agents, packages, report

    def test_base_case_all_packages_delivered(self):
        warehouses, agents, packages, report = self._run("base_case.json")
        total_delivered = sum(a.packages_delivered for a in agents.values())
        self.assertEqual(total_delivered, len(packages))

    def test_test_case_1_all_packages_delivered(self):
        warehouses, agents, packages, report = self._run("test_case_1.json")
        total_delivered = sum(a.packages_delivered for a in agents.values())
        self.assertEqual(total_delivered, len(packages))

    def test_every_package_marked_delivered(self):
        _, _, packages, _ = self._run("base_case.json")
        self.assertTrue(all(pkg.delivered for pkg in packages.values()))

    def test_no_negative_distances(self):
        _, agents, _, _ = self._run("test_case_1.json")
        for agent in agents.values():
            self.assertGreaterEqual(agent.total_distance, 0)

    def test_report_has_best_agent(self):
        _, _, _, report = self._run("base_case.json")
        self.assertIn("best_agent", report)
        self.assertIsNotNone(report["best_agent"])

    def test_report_efficiency_matches_distance_over_delivered(self):
        _, _, _, report = self._run("base_case.json")
        for agent_id, stats in report.items():
            if agent_id == "best_agent":
                continue
            if stats["packages_delivered"] > 0:
# Allow for rounding differences.
                expected = stats["total_distance"] / stats["packages_delivered"]
                self.assertAlmostEqual(stats["efficiency"], expected, delta=0.02)
            else:
                self.assertEqual(stats["efficiency"], 0.0)

    def test_all_provided_test_cases_deliver_every_package(self):
        """
        Runs the full pipeline against EVERY json file in test_cases/
        (base_case + all 10 test_case_N files) and checks the core
        invariant the brief calls out explicitly: total packages
        delivered must equal total packages, for every single one.
        """
        self.assertGreaterEqual(len(ALL_INPUT_FILES), 10, "Expected all provided test cases to be present")
        for fname in ALL_INPUT_FILES:
            with self.subTest(file=fname):
                _, agents, packages, report = self._run(fname)
                total_delivered = sum(a.packages_delivered for a in agents.values())
                self.assertEqual(total_delivered, len(packages), f"{fname}: delivered count mismatch")
                self.assertTrue(all(p.delivered for p in packages.values()), f"{fname}: not all packages marked delivered")
                self.assertTrue(all(a.total_distance >= 0 for a in agents.values()), f"{fname}: negative distance found")

    def test_both_json_schemas_parse(self):
# Check both supported JSON formats.
        w1, a1, p1 = load_data(os.path.join(TEST_CASES_DIR, "base_case.json"))
        w2, a2, p2 = load_data(os.path.join(TEST_CASES_DIR, "test_case_1.json"))
        self.assertTrue(len(w1) > 0 and len(a1) > 0 and len(p1) > 0)
        self.assertTrue(len(w2) > 0 and len(a2) > 0 and len(p2) > 0)


if __name__ == "__main__":
    unittest.main()
