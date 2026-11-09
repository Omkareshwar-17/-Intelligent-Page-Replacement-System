def fifo_page_replacement(reference_string, num_frames):
    """
    Simulates the FIFO Page Replacement Algorithm.

    Parameters:
        reference_string (list): Sequence of page references.
        num_frames (int): Number of available memory frames.

    Returns:
        dict: Simulation results including page faults,
              page hits, hit ratio, fault ratio and history.
    """

    frames = []
    queue_index = 0

    page_faults = 0
    page_hits = 0

    history = []

    for page in reference_string:

        # Page already exists in memory
        if page in frames:
            page_hits += 1
            status = "Hit"

        else:
            page_faults += 1
            status = "Fault"

            # Empty frame available
            if len(frames) < num_frames:
                frames.append(page)

            # Memory is full
            else:
                frames[queue_index] = page

                queue_index = (queue_index + 1) % num_frames

        history.append({
            "page": page,
            "frames": frames.copy(),
            "status": status
        })

    total_references = len(reference_string)

    hit_ratio = (
        page_hits / total_references
        if total_references > 0
        else 0
    )

    fault_ratio = (
        page_faults / total_references
        if total_references > 0
        else 0
    )

    return {
        "algorithm": "FIFO",
        "page_faults": page_faults,
        "page_hits": page_hits,
        "hit_ratio": hit_ratio,
        "fault_ratio": fault_ratio,
        "history": history
    }