import streamlit as st

from simulator.workload import generate_workload
from algorithms.fifo import fifo_page_replacement
from algorithms.lru import lru_page_replacement
from algorithms.adaptive import adaptive, adaptive_auto


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Intelligent Page Replacement System",
    page_icon="🧠",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🧠 Intelligent Page Replacement System")

st.write(
    "Compare traditional page replacement algorithms "
    "with intelligent adaptive page replacement algorithms."
)

st.divider()


# ============================================================
# SYSTEM CONFIGURATION
# ============================================================

st.subheader("⚙️ System Configuration")

frames = st.slider(
    "Number of Frames",
    min_value=2,
    max_value=10,
    value=4
)

pages = st.slider(
    "Number of Pages",
    min_value=5,
    max_value=20,
    value=10
)

length = st.slider(
    "Reference String Length",
    min_value=20,
    max_value=200,
    value=100,
    step=10
)

workload = st.selectbox(
    "Workload Pattern",
    [
        "Locality",
        "Phased",
        "Random",
        "Sequential"
    ]
)


# ============================================================
# CURRENT CONFIGURATION
# ============================================================

st.divider()

st.subheader("📋 Current Configuration")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Frames",
    frames
)

col2.metric(
    "Pages",
    pages
)

col3.metric(
    "References",
    length
)

col4.metric(
    "Pattern",
    workload
)


# ============================================================
# RUN SIMULATION
# ============================================================

st.divider()

if st.button(
    "🚀 Run Simulation",
    type="primary",
    use_container_width=True
):

    # --------------------------------------------------------
    # GENERATE WORKLOAD
    # --------------------------------------------------------

    reference_string = generate_workload(
        pattern=workload.lower(),
        length=length,
        num_pages=pages
    )


    # --------------------------------------------------------
    # RUN ALGORITHMS
    # --------------------------------------------------------

    fifo_result = fifo_page_replacement(
        reference_string,
        frames
    )

    lru_result = lru_page_replacement(
        reference_string,
        frames
    )

    adaptive_result = adaptive(
        reference_string,
        frames,
        alpha=0.5
    )

    auto_result = adaptive_auto(
        reference_string,
        frames,
        window=20
    )


    # --------------------------------------------------------
    # SUCCESS MESSAGE
    # --------------------------------------------------------

    st.success(
        "Simulation completed successfully!"
    )


    # ========================================================
    # REFERENCE STRING
    # ========================================================

    st.subheader("🔢 Generated Reference String")

    st.code(
        " ".join(
            map(str, reference_string)
        )
    )


    # ========================================================
    # ALGORITHM RESULTS
    # ========================================================

    st.divider()

    st.subheader("📊 Algorithm Results")

    fifo_col, lru_col, adaptive_col, auto_col = st.columns(4)


    # FIFO
    with fifo_col:

        st.markdown("### FIFO")

        st.metric(
            "Page Faults",
            fifo_result["page_faults"]
        )

        st.metric(
            "Page Hits",
            fifo_result["page_hits"]
        )

        st.metric(
            "Hit Ratio",
            f'{fifo_result["hit_ratio"] * 100:.2f}%'
        )


    # LRU
    with lru_col:

        st.markdown("### LRU")

        st.metric(
            "Page Faults",
            lru_result["page_faults"]
        )

        st.metric(
            "Page Hits",
            lru_result["page_hits"]
        )

        st.metric(
            "Hit Ratio",
            f'{lru_result["hit_ratio"] * 100:.2f}%'
        )


    # ADAPTIVE
    with adaptive_col:

        st.markdown("### Adaptive")

        st.metric(
            "Page Faults",
            adaptive_result["page_faults"]
        )

        st.metric(
            "Page Hits",
            adaptive_result["page_hits"]
        )

        st.metric(
            "Hit Ratio",
            f'{adaptive_result["hit_ratio"] * 100:.2f}%'
        )


    # ADAPTIVE AUTO
    with auto_col:

        st.markdown("### Adaptive-Auto")

        st.metric(
            "Page Faults",
            auto_result["page_faults"]
        )

        st.metric(
            "Page Hits",
            auto_result["page_hits"]
        )

        st.metric(
            "Hit Ratio",
            f'{auto_result["hit_ratio"] * 100:.2f}%'
        )


    # ========================================================
    # FIND BEST ALGORITHM
    # ========================================================

    results = {
        "FIFO": fifo_result,
        "LRU": lru_result,
        "Adaptive": adaptive_result,
        "Adaptive-Auto": auto_result
    }

    minimum_faults = min(
        result["page_faults"]
        for result in results.values()
    )

    winners = [
        name
        for name, result in results.items()
        if result["page_faults"] == minimum_faults
    ]


    # ========================================================
    # WINNER
    # ========================================================

    st.divider()

    st.subheader("🏆 Best Performing Algorithm")

    if len(winners) == 1:

        st.success(
            f"🏆 {winners[0]} performed best with "
            f"{minimum_faults} page faults."
        )

    else:

        st.info(
            "🤝 Tie between "
            + ", ".join(winners)
            + f" with {minimum_faults} page faults."
        )


    # ========================================================
    # SUMMARY TABLE
    # ========================================================

    st.divider()

    st.subheader("📈 Performance Summary")

    summary_data = {
        "Algorithm": [
            "FIFO",
            "LRU",
            "Adaptive",
            "Adaptive-Auto"
        ],

        "Page Faults": [
            fifo_result["page_faults"],
            lru_result["page_faults"],
            adaptive_result["page_faults"],
            auto_result["page_faults"]
        ],

        "Page Hits": [
            fifo_result["page_hits"],
            lru_result["page_hits"],
            adaptive_result["page_hits"],
            auto_result["page_hits"]
        ],

        "Hit Ratio (%)": [
            round(
                fifo_result["hit_ratio"] * 100,
                2
            ),

            round(
                lru_result["hit_ratio"] * 100,
                2
            ),

            round(
                adaptive_result["hit_ratio"] * 100,
                2
            ),

            round(
                auto_result["hit_ratio"] * 100,
                2
            )
        ]
    }

    st.dataframe(
        summary_data,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # PAGE FAULT CHART
    # ========================================================

    st.subheader("📉 Page Fault Comparison")

    chart_data = {
        "FIFO": fifo_result["page_faults"],
        "LRU": lru_result["page_faults"],
        "Adaptive": adaptive_result["page_faults"],
        "Adaptive-Auto": auto_result["page_faults"]
    }

    st.bar_chart(
        chart_data
    )

    # ========================================================
    # ADAPTIVE-AUTO INTELLIGENCE
    # ========================================================

    st.divider()

    st.subheader("🧠 Adaptive-Auto Intelligence")

    auto_history = auto_result["history"]

    alpha_values = [
        step["alpha"]
        for step in auto_history
    ]

    lru_misses = [
        step["lru_recent_misses"]
        for step in auto_history
    ]

    lfu_misses = [
        step["lfu_recent_misses"]
        for step in auto_history
    ]

    final_alpha = alpha_values[-1]
    average_alpha = sum(alpha_values) / len(alpha_values)

    intel_col1, intel_col2, intel_col3 = st.columns(3)

    intel_col1.metric(
        "Final Alpha",
        f"{final_alpha:.2f}"
    )

    intel_col2.metric(
        "Average Alpha",
        f"{average_alpha:.2f}"
    )

    if final_alpha > 0.55:
        strategy = "Frequency-Oriented"
    elif final_alpha < 0.45:
        strategy = "Recency-Oriented"
    else:
        strategy = "Balanced"

    intel_col3.metric(
        "Current Strategy",
        strategy
    )


    # ========================================================
    # EXPLANATION
    # ========================================================

    if final_alpha > 0.55:

        st.info(
            "📊 Adaptive-Auto detected that frequency-based "
            "replacement is currently performing better. "
            "It therefore gives more importance to page frequency."
        )

    elif final_alpha < 0.45:

        st.info(
            "⚡ Adaptive-Auto detected that recent page usage "
            "is more important for this workload. "
            "It therefore gives more importance to recency."
        )

    else:

        st.info(
            "⚖️ Adaptive-Auto is currently balancing frequency "
            "and recency because neither strategy has a strong advantage."
        )


    # ========================================================
    # ALPHA GRAPH
    # ========================================================

    st.subheader("📈 Alpha Adaptation Over Time")

    alpha_chart = {
        "Alpha": alpha_values
    }

    st.line_chart(
        alpha_chart
    )


    # ========================================================
    # SHADOW ALGORITHM GRAPH
    # ========================================================

    st.subheader("🔍 Shadow Algorithm Performance")

    shadow_chart = {
        "LRU Recent Misses": lru_misses,
        "LFU Recent Misses": lfu_misses
    }

    st.line_chart(
        shadow_chart
    )

    # ========================================================
    # EVICTION DECISION EXPLORER
    # ========================================================

    st.divider()

    st.subheader("🔬 Eviction Decision Explorer")

    st.write(
        "Inspect how Adaptive-Auto selected a victim page "
        "during each page replacement."
    )


    # --------------------------------------------------------
    # FIND ONLY STEPS WHERE AN EVICTION OCCURRED
    # --------------------------------------------------------

    eviction_steps = [
        (index, step)
        for index, step in enumerate(auto_history)
        if step["evicted"] is not None
    ]


    if eviction_steps:

        # Create readable options for the dropdown
        eviction_options = {
            f"Reference {index + 1} — Page {step['page']}":
            (index, step)
            for index, step in eviction_steps
        }


        selected_label = st.selectbox(
            "Select an eviction event",
            list(eviction_options.keys())
        )


        selected_index, selected_step = (
            eviction_options[selected_label]
        )


        # ----------------------------------------------------
        # BASIC DECISION INFORMATION
        # ----------------------------------------------------

        st.markdown("### 🧠 Decision Details")

        decision_col1, decision_col2, decision_col3 = st.columns(3)


        decision_col1.metric(
            "Requested Page",
            selected_step["page"]
        )


        decision_col2.metric(
            "Evicted Page",
            selected_step["evicted"]
        )


        decision_col3.metric(
            "Alpha",
            f'{selected_step["alpha"]:.3f}'
        )


        # ----------------------------------------------------
        # FRAME STATE
        # ----------------------------------------------------

        st.markdown("### 🗂️ Frames After Replacement")

        st.code(
            "  ".join(
                map(
                    str,
                    selected_step["frames"]
                )
            )
        )


        # ----------------------------------------------------
        # PAGE SCORES
        # ----------------------------------------------------

        scores = selected_step["scores"]

        if scores:

            st.markdown(
                "### 📊 Candidate Page Scores"
            )

            score_table = []

            for page, score in scores.items():

                score_table.append({
                    "Page": page,
                    "Combined Score": round(
                        score,
                        4
                    ),
                    "Decision": (
                        "Evicted"
                        if page == selected_step["evicted"]
                        else "Kept"
                    )
                })


            st.dataframe(
                score_table,
                use_container_width=True,
                hide_index=True
            )


            # ------------------------------------------------
            # FIND LOWEST SCORE
            # ------------------------------------------------

            lowest_page = min(
                scores,
                key=scores.get
            )

            lowest_score = scores[
                lowest_page
            ]


            # ------------------------------------------------
            # EXPLANATION
            # ------------------------------------------------

            st.markdown(
                "### 💡 Why Was This Page Evicted?"
            )

            st.info(
                f"Page {selected_step['evicted']} was selected "
                f"for replacement because it had one of the "
                f"lowest combined frequency-recency scores "
                f"({lowest_score:.4f}). "
                f"The current alpha value was "
                f"{selected_step['alpha']:.3f}."
            )


            # ------------------------------------------------
            # ALPHA INTERPRETATION
            # ------------------------------------------------

            alpha = selected_step["alpha"]

            if alpha > 0.55:

                st.write(
                    "At this moment, the algorithm was giving "
                    "**more importance to frequency** than recency."
                )

            elif alpha < 0.45:

                st.write(
                    "At this moment, the algorithm was giving "
                    "**more importance to recency** than frequency."
                )

            else:

                st.write(
                    "At this moment, the algorithm was using a "
                    "**balanced combination of frequency and recency**."
                )


            # ------------------------------------------------
            # SHADOW CACHE INFORMATION
            # ------------------------------------------------

            st.markdown(
                "### 👥 Shadow Algorithm State"
            )

            shadow_col1, shadow_col2 = st.columns(2)

            shadow_col1.metric(
                "LRU Recent Misses",
                selected_step[
                    "lru_recent_misses"
                ]
            )

            shadow_col2.metric(
                "LFU Recent Misses",
                selected_step[
                    "lfu_recent_misses"
                ]
            )


    else:

        st.info(
            "No eviction occurred during this simulation."
        )