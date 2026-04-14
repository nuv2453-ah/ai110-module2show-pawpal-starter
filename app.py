"""
app.py — PawPal+ Streamlit application

Two tabs:
  📅 Daily Schedule — add/manage pet care tasks, detect conflicts
  🤖 Ask PawPal AI  — RAG-powered Q&A using the Claude API
"""

import streamlit as st
from datetime import datetime, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler
from pawpal_ai import ask_pawpal, build_index

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+ — Smart Pet Care Assistant")

# ---------------------------------------------------------------------------
# Build RAG index once per session (cached across reruns)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading knowledge base...")
def get_rag_index():
    return build_index()


# ---------------------------------------------------------------------------
# Sidebar: Pet profile
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Pet Profile")
    owner_name = st.text_input("Owner name", value="Jordan")
    pet_name   = st.text_input("Pet name",   value="Mochi")
    species    = st.selectbox("Species", ["dog", "cat", "other"])
    age        = st.number_input("Pet age (years)", min_value=0, max_value=30, value=3)
    st.divider()
    st.caption("PawPal+ uses AI to answer pet care questions from a curated knowledge base.")

# ---------------------------------------------------------------------------
# Shared owner/scheduler state
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    owner = Owner(owner_name, "")
    pet   = Pet(pet_name, species, int(age))
    owner.add_pet(pet)
    st.session_state.owner     = owner
    st.session_state.scheduler = Scheduler()
    st.session_state.scheduler.load_tasks_from_owner(owner)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_schedule, tab_ai = st.tabs(["📅 Daily Schedule", "🤖 Ask PawPal AI"])

# ===== TAB 1: Daily Schedule ================================================
with tab_schedule:
    st.subheader(f"Daily Schedule for {pet_name}")

    # --- Add task form ---
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_type = st.text_input("Task", value="Morning walk")
        with col2:
            hour = st.selectbox("Hour", list(range(0, 24)), index=8)
            minute = st.selectbox("Minute", [0, 15, 30, 45])
        with col3:
            priority = st.slider("Priority (1=low, 3=high)", 1, 3, 2)
        with col4:
            recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])

        submitted = st.form_submit_button("➕ Add Task")
        if submitted and task_type.strip():
            task_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            rec = recurrence if recurrence != "none" else None
            new_task = Task(task_type.strip(), task_time, priority, recurrence=rec)

            # Add to the first pet for simplicity
            st.session_state.owner.pets[0].add_task(new_task)
            st.session_state.scheduler.load_tasks_from_owner(st.session_state.owner)
            st.session_state.scheduler.sort_tasks()
            st.success(f"Added task: {task_type} at {task_time.strftime('%H:%M')}")

    st.divider()

    # --- Today's tasks ---
    today_tasks = st.session_state.scheduler.get_today_tasks()

    if not today_tasks:
        st.info("No tasks scheduled for today. Add one above.")
    else:
        st.markdown("### Today's Tasks")
        for i, task in enumerate(today_tasks):
            col_time, col_type, col_pri, col_rec, col_status, col_btn = st.columns(
                [1, 2, 1, 1, 1, 1]
            )
            col_time.write(task.time.strftime("%H:%M") if task.time else "—")
            col_type.write(task.task_type.title())
            col_pri.write("⭐" * task.priority)
            col_rec.write(task.recurrence or "—")
            col_status.write("✅ Done" if task.done else "⏳ Pending")

            if not task.done:
                if col_btn.button("Complete", key=f"complete_{i}"):
                    st.session_state.scheduler.complete_task(task)
                    st.rerun()

    # --- Conflict detection ---
    conflicts = st.session_state.scheduler.detect_conflicts()
    if conflicts:
        st.divider()
        st.error("⚠️ Schedule Conflicts Detected")
        for t1, t2 in conflicts:
            st.write(
                f"**{t1.task_type}** and **{t2.task_type}** are both scheduled at "
                f"{t1.time.strftime('%H:%M') if t1.time else '?'}"
            )

    # --- Filter incomplete ---
    with st.expander("Show only pending tasks"):
        pending = st.session_state.scheduler.filter_by_status(done=False)
        if pending:
            for t in pending:
                st.write(
                    f"• {t.time.strftime('%H:%M') if t.time else '?'} — "
                    f"{t.task_type.title()} (priority {t.priority})"
                )
        else:
            st.write("All tasks completed!")


# ===== TAB 2: Ask PawPal AI =================================================
with tab_ai:
    st.subheader("Ask PawPal AI")
    st.caption(
        "PawPal+ retrieves relevant pet care information from its knowledge base, "
        "then uses Claude to generate a grounded answer."
    )

    question = st.text_input(
        "Your question",
        placeholder="e.g. How often should I feed my dog? Is ibuprofen safe for cats?",
    )

    ask_btn = st.button("Ask PawPal", type="primary", disabled=not question.strip())

    if ask_btn and question.strip():
        index = get_rag_index()
        with st.spinner("Searching knowledge base and consulting AI..."):
            result = ask_pawpal(
                question,
                pet_name=pet_name,
                species=species if species != "other" else "",
                index=index,
            )

        if not result["safe"]:
            st.error(result["answer"])
        elif result["error"]:
            st.warning(result["answer"])
        else:
            st.markdown("### Answer")
            st.markdown(result["answer"])

            # Confidence badge
            conf = result["confidence"]
            conf_color = "green" if conf >= 0.7 else "orange" if conf >= 0.4 else "red"
            st.markdown(
                f"**Confidence:** :{conf_color}[{conf:.0%}]"
            )

            # Sources (RAG transparency)
            if result["sources"]:
                with st.expander("📚 Sources used from knowledge base"):
                    for src in result["sources"]:
                        st.write(f"• `{src.replace('_', ' ').title()}`")
            else:
                st.caption("No knowledge base documents matched this query.")

    # --- Sample questions ---
    with st.expander("💡 Try these example questions"):
        examples = [
            "How often should I feed my adult dog?",
            "Is ibuprofen safe to give my cat?",
            "What should I do if my pet misses a medication dose?",
            "How much exercise does my dog need each day?",
            "What are signs that my cat might be sick?",
        ]
        for ex in examples:
            st.write(f"• {ex}")
