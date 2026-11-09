from collections import deque, OrderedDict


# ============================================================
# VICTIM SELECTION
# ============================================================

def _choose_victim(frames, freq, last_used, time, alpha):
    """
    Score every page currently in memory.

    Score is based on:
        1. Frequency - how often the page has been used
        2. Recency   - how recently the page was used

    alpha controls the balance:

        alpha close to 1 -> favor frequency
        alpha close to 0 -> favor recency

    The page with the LOWEST score is evicted.

    Returns:
        victim_page, scores
    """

    max_freq = max(freq[p] for p in frames)

    max_age = max(
        time - last_used[p]
        for p in frames
    )

    scores = {}

    for p in frames:

        # -------------------------
        # Frequency score
        # -------------------------

        freq_score = freq[p] / max_freq

        # -------------------------
        # Recency score
        # -------------------------

        age = time - last_used[p]

        if max_age > 0:
            recency_score = 1 - (age / max_age)
        else:
            recency_score = 1.0

        # -------------------------
        # Combined score
        # -------------------------

        scores[p] = (
            alpha * freq_score
            + (1 - alpha) * recency_score
        )

    # Lowest score loses.
    # If scores are equal, evict the least recently used page.
    victim = min(
        frames,
        key=lambda p: (
            scores[p],
            last_used[p]
        )
    )

    return victim, scores


# ============================================================
# FIXED-WEIGHT ADAPTIVE ALGORITHM
# ============================================================

def adaptive(reference_string, num_frames, alpha=0.5):
    """
    Adaptive Page Replacement Algorithm.

    Uses a combination of:

        Frequency + Recency

    alpha determines their relative importance.

    Example:

        alpha = 0.7

    means:

        70% Frequency
        30% Recency
    """

    if num_frames < 1:
        raise ValueError(
            "num_frames must be at least 1"
        )

    if not 0 <= alpha <= 1:
        raise ValueError(
            "alpha must be between 0 and 1"
        )

    frames = []

    # Frequency of pages currently in memory
    freq = {}

    # Most recent access time
    last_used = {}

    faults = 0
    hits = 0

    history = []

    # --------------------------------------------------------
    # PROCESS REFERENCE STRING
    # --------------------------------------------------------

    for time, page in enumerate(reference_string):

        evicted = None
        scores = None

        # ====================================================
        # PAGE HIT
        # ====================================================

        if page in frames:

            hits += 1
            status = "Hit"

            freq[page] += 1
            last_used[page] = time

        # ====================================================
        # PAGE FAULT
        # ====================================================

        else:

            faults += 1
            status = "Fault"

            # Memory is full
            if len(frames) == num_frames:

                evicted, scores = _choose_victim(
                    frames,
                    freq,
                    last_used,
                    time,
                    alpha
                )

                frames.remove(evicted)

                del freq[evicted]
                del last_used[evicted]

            # Add new page
            frames.append(page)

            freq[page] = 1
            last_used[page] = time

        # ----------------------------------------------------
        # SAVE HISTORY
        # ----------------------------------------------------

        history.append({
            "page": page,
            "frames": list(frames),
            "status": status,
            "evicted": evicted,
            "scores": scores,
            "alpha": alpha,
        })

    # ========================================================
    # RESULTS
    # ========================================================

    total = len(reference_string)

    return {
        "algorithm": "Adaptive",
        "page_faults": faults,
        "page_hits": hits,
        "hit_ratio": hits / total if total else 0,
        "fault_ratio": faults / total if total else 0,
        "history": history,
    }


# ============================================================
# SHADOW LRU
# ============================================================

class _ShadowLRU:
    """
    Lightweight LRU cache used only for observing
    how well LRU would perform on the workload.

    It does NOT control the real page frames.
    """

    def __init__(self, size):

        self.size = size
        self.pages = OrderedDict()

    def access(self, page):

        # -------------------------
        # HIT
        # -------------------------

        if page in self.pages:

            self.pages.move_to_end(page)

            return True

        # -------------------------
        # MISS
        # -------------------------

        if len(self.pages) == self.size:

            self.pages.popitem(
                last=False
            )

        self.pages[page] = True

        return False


# ============================================================
# SHADOW LFU
# ============================================================

class _ShadowLFU:
    """
    Lightweight LFU cache.

    Used to estimate whether frequency-based
    replacement is currently performing well.

    Tie breaking:
        Least recently used page is removed.
    """

    def __init__(self, size):

        self.size = size

        self.freq = {}
        self.last = {}

        self.t = 0

    def access(self, page):

        self.t += 1

        # -------------------------
        # HIT
        # -------------------------

        if page in self.freq:

            self.freq[page] += 1
            self.last[page] = self.t

            return True

        # -------------------------
        # MISS
        # -------------------------

        if len(self.freq) == self.size:

            victim = min(
                self.freq,
                key=lambda p: (
                    self.freq[p],
                    self.last[p]
                )
            )

            del self.freq[victim]
            del self.last[victim]

        self.freq[page] = 1
        self.last[page] = self.t

        return False


# ============================================================
# SELF-TUNING ADAPTIVE ALGORITHM
# ============================================================

def adaptive_auto(
    reference_string,
    num_frames,
    window=20
):
    """
    Self-Tuning Adaptive Page Replacement Algorithm.

    Unlike adaptive(), alpha is NOT fixed.

    Two shadow algorithms are monitored:

        Shadow LRU
        Shadow LFU

    Their recent performance determines alpha.

    If LRU performs better:
        algorithm gives more importance to recency.

    If LFU performs better:
        algorithm gives more importance to frequency.

    window controls how many recent accesses are used
    when calculating performance.
    """

    if num_frames < 1:
        raise ValueError(
            "num_frames must be at least 1"
        )

    if window < 1:
        raise ValueError(
            "window must be at least 1"
        )

    # --------------------------------------------------------
    # SHADOW ALGORITHMS
    # --------------------------------------------------------

    shadow_lru = _ShadowLRU(
        num_frames
    )

    shadow_lfu = _ShadowLFU(
        num_frames
    )

    # 1 = miss
    # 0 = hit

    lru_misses = deque(
        maxlen=window
    )

    lfu_misses = deque(
        maxlen=window
    )

    # --------------------------------------------------------
    # REAL CACHE
    # --------------------------------------------------------

    frames = []

    freq = {}
    last_used = {}

    faults = 0
    hits = 0

    history = []

    # --------------------------------------------------------
    # PROCESS REFERENCES
    # --------------------------------------------------------

    for time, page in enumerate(reference_string):

        # ====================================================
        # UPDATE SHADOW ALGORITHMS
        # ====================================================

        lru_hit = shadow_lru.access(page)
        lfu_hit = shadow_lfu.access(page)

        lru_misses.append(
            0 if lru_hit else 1
        )

        lfu_misses.append(
            0 if lfu_hit else 1
        )

        # Number of recent misses
        lru_miss_count = sum(
            lru_misses
        )

        lfu_miss_count = sum(
            lfu_misses
        )

        # ====================================================
        # AUTOMATIC ALPHA
        # ====================================================

        alpha = (
            (lru_miss_count + 1)
            /
            (
                lru_miss_count
                + lfu_miss_count
                + 2
            )
        )

        evicted = None
        scores = None

        # ====================================================
        # PAGE HIT
        # ====================================================

        if page in frames:

            hits += 1
            status = "Hit"

            freq[page] += 1
            last_used[page] = time

        # ====================================================
        # PAGE FAULT
        # ====================================================

        else:

            faults += 1
            status = "Fault"

            # Memory full
            if len(frames) == num_frames:

                evicted, scores = _choose_victim(
                    frames,
                    freq,
                    last_used,
                    time,
                    alpha
                )

                frames.remove(
                    evicted
                )

                del freq[evicted]
                del last_used[evicted]

            # Add requested page
            frames.append(page)

            freq[page] = 1
            last_used[page] = time

        # ====================================================
        # SAVE HISTORY
        # ====================================================

        history.append({
            "page": page,
            "frames": list(frames),
            "status": status,
            "evicted": evicted,
            "scores": scores,
            "alpha": alpha,
            "lru_recent_misses": lru_miss_count,
            "lfu_recent_misses": lfu_miss_count,
        })

    # ========================================================
    # FINAL RESULTS
    # ========================================================

    total = len(reference_string)

    return {
        "algorithm": "Adaptive-Auto",
        "page_faults": faults,
        "page_hits": hits,
        "hit_ratio": hits / total if total else 0,
        "fault_ratio": faults / total if total else 0,
        "history": history,
    }