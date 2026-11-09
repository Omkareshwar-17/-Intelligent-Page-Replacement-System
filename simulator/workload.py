import random


def generate_random_workload(length=30, num_pages=10):
    """Completely random page references."""
    return [random.randint(0, num_pages - 1) for _ in range(length)]


def generate_sequential_workload(length=30, num_pages=10):
    """Pages accessed in order: 0, 1, 2, ..., num_pages-1, 0, 1, ..."""
    return [i % num_pages for i in range(length)]


def generate_locality_workload(length=30, num_pages=10, locality_size=3):
    """
    Locality of reference: ~80% of accesses come from a small
    working set, ~20% go to any page.
    """
    locality_size = min(locality_size, num_pages)
    working_set = random.sample(range(num_pages), locality_size)

    reference_string = []
    for _ in range(length):
        if random.random() < 0.8:
            page = random.choice(working_set)
        else:
            page = random.randint(0, num_pages - 1)
        reference_string.append(page)

    return reference_string


def generate_workload(pattern="random", length=30, num_pages=10, locality_size=3):
    """Single entry point used by the rest of the project."""
    pattern = pattern.lower()

    if pattern == "random":
        return generate_random_workload(length, num_pages)
    elif pattern == "sequential":
        return generate_sequential_workload(length, num_pages)
    elif pattern == "locality":
        return generate_locality_workload(length, num_pages, locality_size)
    elif pattern == "phased":
        return generate_phased_workload(length, num_pages, locality_size)
    else:
        raise ValueError(
            f"Unknown pattern '{pattern}'. Use 'random', 'sequential', "
            f"'locality' or 'phased'."
        )

def generate_phased_workload(length=100, num_pages=10,
                             locality_size=3, phase_length=25):
    """
    Locality with phase changes: the working set is replaced
    every `phase_length` accesses.
    """
    locality_size = min(locality_size, num_pages)
    working_set = random.sample(range(num_pages), locality_size)

    reference_string = []
    for i in range(length):
        if i > 0 and i % phase_length == 0:
            working_set = random.sample(range(num_pages), locality_size)

        if random.random() < 0.8:
            page = random.choice(working_set)
        else:
            page = random.randint(0, num_pages - 1)
        reference_string.append(page)

    return reference_string