from simulator.workload import generate_workload


def run_algorithms(algorithms, reference_string, num_frames):
    """
    Run every algorithm on ONE reference string.

    algorithms: dict like {"FIFO": fifo, "LRU": lru}
    Returns: dict {name: result}
    """
    return {
        name: func(reference_string, num_frames)
        for name, func in algorithms.items()
    }


def benchmark(algorithms, patterns=("random", "sequential", "locality"),
              length=100, num_pages=10, num_frames=4, trials=30):
    """
    Run all algorithms on many generated workloads and average the results.

    Returns a dict:
        {pattern: {algorithm_name: {"avg_faults": ..., "avg_hit_ratio": ...}}}
    """
    summary = {}

    for pattern in patterns:
        totals = {name: {"faults": 0, "hit_ratio": 0.0} for name in algorithms}

        for _ in range(trials):
            workload = generate_workload(pattern, length, num_pages)

            # Same workload goes to every algorithm -> fair comparison
            results = run_algorithms(algorithms, workload, num_frames)

            for name, result in results.items():
                totals[name]["faults"] += result["faults"]
                totals[name]["hit_ratio"] += result["hit_ratio"]

        summary[pattern] = {
            name: {
                "avg_faults": totals[name]["faults"] / trials,
                "avg_hit_ratio": totals[name]["hit_ratio"] / trials,
            }
            for name in algorithms
        }

    return summary


def print_summary(summary):
    """Print the benchmark results as a readable table."""
    for pattern, results in summary.items():
        print(f"\n=== {pattern.upper()} workload ===")
        print(f"{'Algorithm':<12}{'Avg faults':>12}{'Avg hit ratio':>16}")
        for name, values in results.items():
            print(f"{name:<12}{values['avg_faults']:>12.1f}"
                  f"{values['avg_hit_ratio']:>16.2f}")

def sweep_alpha(adaptive_func, pattern="locality", alphas=None,
                length=100, num_pages=10, num_frames=4, trials=50):
    """
    Try different alpha values for the adaptive algorithm.

    Every alpha sees the same workloads, so the comparison is fair.
    Returns {alpha: average_faults}.
    """
    if alphas is None:
        alphas = [i / 10 for i in range(11)]   # 0.0, 0.1, ..., 1.0

    totals = {a: 0 for a in alphas}

    for _ in range(trials):
        workload = generate_workload(pattern, length, num_pages)
        for a in alphas:
            totals[a] += adaptive_func(workload, num_frames, alpha=a)["faults"]

    return {a: totals[a] / trials for a in alphas}