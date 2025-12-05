"""
scripts/collect_metrics.py

Utility hooks to collect simulation metrics and export them to CSV.
Attach these helpers in VehicleAgent and CoordinatorAgent to log:
- Route recalculation latency per vehicle on blocked_edges_update
- Original vs recalculated route cost to estimate detour length factor
- Semaphore penalty share in total route cost

Usage example:
from scripts.collect_metrics import MetricsCollector
metrics = MetricsCollector(output_dir="metrics")
metrics.log_recalc_latency(vehicle_id, start_ts, end_ts)
metrics.log_route_costs(vehicle_id, original_cost, new_cost)
metrics.log_semaphore_penalty(vehicle_id, base_cost, penalty_cost)
metrics.flush()
"""

import csv
import os
from dataclasses import dataclass, field
from typing import List, Tuple
import statistics


@dataclass
class MetricsCollector:
    output_dir: str = "metrics"
    recalc_latency_rows: List[Tuple[str, float]] = field(default_factory=list)
    route_cost_rows: List[Tuple[str, float, float, float]] = field(default_factory=list)
    semaphore_penalty_rows: List[Tuple[str, float, float, float]] = field(default_factory=list)
    traffic_penalty_rows: List[Tuple[str, float, float, float]] = field(default_factory=list)

    def __post_init__(self):
        os.makedirs(self.output_dir, exist_ok=True)

    def log_recalc_latency(self, vehicle_id: str, start_ts: float, end_ts: float) -> None:
        latency_ms = (end_ts - start_ts) * 1000.0
        self.recalc_latency_rows.append((vehicle_id, latency_ms))

    def log_route_costs(self, vehicle_id: str, original_cost: float, new_cost: float) -> None:
        if original_cost <= 0:
            factor = 0.0
        else:
            factor = new_cost / original_cost
        self.route_cost_rows.append((vehicle_id, original_cost, new_cost, factor))

    def log_semaphore_penalty(self, vehicle_id: str, base_cost: float, penalty_cost: float) -> None:
        total = base_cost + penalty_cost
        share = 0.0 if total <= 0 else penalty_cost / total
        self.semaphore_penalty_rows.append((vehicle_id, base_cost, penalty_cost, share))

    def log_traffic_penalty(self, vehicle_id: str, base_cost: float, penalty_cost: float) -> None:
        total = base_cost + penalty_cost
        share = 0.0 if total <= 0 else penalty_cost / total
        self.traffic_penalty_rows.append((vehicle_id, base_cost, penalty_cost, share))

    def flush(self) -> None:
        self._write_csv(
            os.path.join(self.output_dir, "recalc_latency.csv"),
            ["vehicle_id", "latency_ms"],
            self.recalc_latency_rows,
        )
        self._write_csv(
            os.path.join(self.output_dir, "route_costs.csv"),
            ["vehicle_id", "original_cost", "new_cost", "detour_factor"],
            self.route_cost_rows,
        )
        self._write_csv(
            os.path.join(self.output_dir, "semaphore_penalty.csv"),
            ["vehicle_id", "base_cost", "penalty_cost", "penalty_share"],
            self.semaphore_penalty_rows,
        )
        self._write_csv(
            os.path.join(self.output_dir, "traffic_penalty.csv"),
            ["vehicle_id", "base_cost", "penalty_cost", "penalty_share"],
            self.traffic_penalty_rows,
        )
        self._write_summary()

    def _write_csv(self, path: str, headers: List[str], rows: List[Tuple]) -> None:
        if not rows:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    def _write_summary(self) -> None:
        path = os.path.join(self.output_dir, "summary.csv")
        rows = []
        # Latency stats
        if self.recalc_latency_rows:
            latencies = [r[1] for r in self.recalc_latency_rows]
            rows.append(["recalc_latency_ms_avg", f"{statistics.fmean(latencies):.2f}"])
            rows.append(["recalc_latency_ms_p50", f"{statistics.median(latencies):.2f}"])
            rows.append(["recalc_latency_ms_p95", f"{_percentile(latencies, 95):.2f}"])
        # Detour factor stats
        if self.route_cost_rows:
            detours = [r[3] for r in self.route_cost_rows if r[3] > 0]
            if detours:
                rows.append(["detour_factor_avg", f"{statistics.fmean(detours):.3f}"])
                rows.append(["detour_factor_p50", f"{statistics.median(detours):.3f}"])
                rows.append(["detour_factor_p95", f"{_percentile(detours, 95):.3f}"])
        # Penalty shares
        if self.semaphore_penalty_rows:
            shares = [r[3] for r in self.semaphore_penalty_rows]
            rows.append(["semaphore_penalty_share_avg", f"{statistics.fmean(shares):.4f}"])
        if self.traffic_penalty_rows:
            shares = [r[3] for r in self.traffic_penalty_rows]
            rows.append(["traffic_penalty_share_avg", f"{statistics.fmean(shares):.4f}"])
        if not rows:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            writer.writerows(rows)


def _percentile(data: List[float], p: int) -> float:
    if not data:
        return 0.0
    data_sorted = sorted(data)
    k = (len(data_sorted)-1) * (p/100)
    f = int(k)
    c = min(f + 1, len(data_sorted) - 1)
    if f == c:
        return data_sorted[int(k)]
    return data_sorted[f] + (k - f) * (data_sorted[c] - data_sorted[f])


if __name__ == "__main__":
    # Simple sanity run
    mc = MetricsCollector()
    mc.log_recalc_latency("v1", 0.001, 0.045)
    mc.log_route_costs("v1", 100.0, 135.0)
    mc.log_semaphore_penalty("v1", 120.0, 15.0)
    mc.flush()
    print(f"CSV files written to {mc.output_dir}")
