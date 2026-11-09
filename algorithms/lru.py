def lru_page_replacement(reference_string, num_frames):
    """
    Simulates the LRU (Least Recently Used)
    Page Replacement Algorithm.
    """

    frames = []

    page_faults = 0
    page_hits = 0

    # Stores when each page was last used
    last_used = {}

    history = []

    for current_time, page in enumerate(reference_string):

        # -------------------------
        # PAGE HIT
        # -------------------------
        if page in frames:

            page_hits += 1
            status = "Hit"

        # -------------------------
        # PAGE FAULT
        # -------------------------
        else:

            page_faults += 1
            status = "Fault"

            # Empty frame available
            if len(frames) < num_frames:

                frames.append(page)

            # Frames are full
            else:

                # Find least recently used page
                lru_page = min(
                    frames,
                    key=lambda p: last_used[p]
                )

                # Replace LRU page
                replace_index = frames.index(lru_page)

                frames[replace_index] = page

        # Update last-used time
        last_used[page] = current_time

        # Store simulation history
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
        "algorithm": "LRU",
        "page_faults": page_faults,
        "page_hits": page_hits,
        "hit_ratio": hit_ratio,
        "fault_ratio": fault_ratio,
        "history": history
    }