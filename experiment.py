import random
import statistics

from algorithms.fifo import fifo_page_replacement
from algorithms.lru import lru_page_replacement
from algorithms.adaptive import adaptive, adaptive_auto
from simulator.workload import generate_workload


# ============================================================
# BENCHMARK CONFIGURATION
# ============================================================

NUM_FRAMES = 4
NUM_PAGES = 10
REFERENCE_LENGTH = 100

NUM_RUNS = 100

RANDOM_SEED = 42

PATTERNS = [
    "random",
    "sequential",
    "locality",
    "phased"
]


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(RANDOM_SEED)


# ============================================================
# HEADER
# ============================================================

print("\n==============================================================")
print(" INTELLIGENT PAGE REPLACEMENT - ADVANCED BENCHMARK")
print("==============================================================")

print(f"Frames            : {NUM_FRAMES}")
print(f"Pages             : {NUM_PAGES}")
print(f"Reference Length  : {REFERENCE_LENGTH}")
print(f"Runs per Workload : {NUM_RUNS}")
print(f"Random Seed       : {RANDOM_SEED}")


# ============================================================
# TEST EACH WORKLOAD
# ============================================================

for pattern in PATTERNS:

    fault_results = {
        "FIFO": [],
        "LRU": [],
        "Adaptive": [],
        "Adaptive-Auto": []
    }

    wins = {
        "FIFO": 0,
        "LRU": 0,
        "Adaptive": 0,
        "Adaptive-Auto": 0
    }


    # ========================================================
    # RUN BENCHMARK
    # ========================================================

    for _ in range(NUM_RUNS):

        # One workload is generated and shared by all algorithms
        reference_string = generate_workload(
            pattern=pattern,
            length=REFERENCE_LENGTH,
            num_pages=NUM_PAGES
        )


        fifo_result = fifo_page_replacement(
            reference_string,
            NUM_FRAMES
        )


        lru_result = lru_page_replacement(
            reference_string,
            NUM_FRAMES
        )


        adaptive_result = adaptive(
            reference_string,
            NUM_FRAMES,
            alpha=0.5
        )


        auto_result = adaptive_auto(
            reference_string,
            NUM_FRAMES,
            window=20
        )


        current_faults = {
            "FIFO": fifo_result["page_faults"],
            "LRU": lru_result["page_faults"],
            "Adaptive": adaptive_result["page_faults"],
            "Adaptive-Auto": auto_result["page_faults"]
        }


        # Store faults
        for algorithm, faults in current_faults.items():
            fault_results[algorithm].append(faults)


        # ====================================================
        # FIND WINNER FOR THIS RUN
        # ====================================================

        minimum_faults = min(
            current_faults.values()
        )

        current_winners = [
            algorithm
            for algorithm, faults in current_faults.items()
            if faults == minimum_faults
        ]


        # Give each tied winner one win.
        # We'll explicitly describe this as "best-result rate".
        for algorithm in current_winners:
            wins[algorithm] += 1


    # ========================================================
    # RESULTS
    # ========================================================

    print("\n--------------------------------------------------------------")
    print(f"WORKLOAD: {pattern.upper()}")
    print("--------------------------------------------------------------")

    print(
        f"{'Algorithm':<16}"
        f"{'Avg Faults':>12}"
        f"{'Std Dev':>12}"
        f"{'Best Rate':>14}"
    )

    print("-" * 54)


    averages = {}


    for algorithm, values in fault_results.items():

        average = statistics.mean(values)

        std_dev = statistics.stdev(values)

        best_rate = (
            wins[algorithm] / NUM_RUNS
        ) * 100

        averages[algorithm] = average


        print(
            f"{algorithm:<16}"
            f"{average:>12.2f}"
            f"{std_dev:>12.2f}"
            f"{best_rate:>13.2f}%"
        )


    # ========================================================
    # IMPROVEMENT VS LRU
    # ========================================================

    lru_average = averages["LRU"]

    adaptive_average = averages["Adaptive"]

    auto_average = averages["Adaptive-Auto"]


    if lru_average > 0:

        adaptive_improvement = (
            (lru_average - adaptive_average)
            / lru_average
        ) * 100


        auto_improvement = (
            (lru_average - auto_average)
            / lru_average
        ) * 100

    else:

        adaptive_improvement = 0
        auto_improvement = 0


    print("\nImprovement compared with LRU:")

    print(
        f"Adaptive      : "
        f"{adaptive_improvement:+.2f}%"
    )

    print(
        f"Adaptive-Auto : "
        f"{auto_improvement:+.2f}%"
    )


print("\n==============================================================")
print(" BENCHMARK COMPLETE")
print("==============================================================")