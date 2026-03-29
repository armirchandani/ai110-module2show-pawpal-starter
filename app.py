import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Your daily pet care planner.")

# ── Session State Setup ──────────────────────────────────────────────────────
# Streamlit reruns top-to-bottom on every interaction, so we store the Owner
# object in session_state so it persists across button clicks.
if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Step 1: Owner + Pet Setup ────────────────────────────────────────────────
st.subheader("👤 Owner Info")

owner_name = st.text_input("Your name", value="Aastha")
time_available = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=120)
preferences = st.text_input("Preferences (optional, e.g. 'morning walks, no tasks after 8pm')", value="")

st.subheader("🐾 Pet Info")
pet_name = st.text_input("Pet name", value="Max")
species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])

if st.button("Set up owner & pet"):
    pet = Pet(name=pet_name, species=species)
    prefs = [p.strip() for p in preferences.split(",")] if preferences else []
    owner = Owner(name=owner_name, time_available_minutes=int(time_available), preferences=prefs)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.success(f"✅ {owner_name} and {pet_name} are ready!")

st.divider()

# ── Step 2: Add Tasks ────────────────────────────────────────────────────────
st.subheader("📋 Add Tasks")

if st.session_state.owner is None:
    st.info("Set up your owner and pet above first.")
else:
    owner = st.session_state.owner

    col1, col2 = st.columns(2)
    with col1:
        task_name = st.text_input("Task name", value="Morning Walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
    with col2:
        priority = st.selectbox("Priority", ["high", "medium", "low"])
        time = st.text_input("Preferred time (HH:MM)", value="08:00")
        pet_choice = st.selectbox("Assign to pet", [p.name for p in owner.pets])

    if st.button("Add task"):
        task = Task(
            name=task_name,
            duration_minutes=int(duration),
            priority=priority,
            time=time,
            frequency=frequency
        )
        for pet in owner.pets:
            if pet.name == pet_choice:
                pet.add_task(task)
        st.success(f"✅ '{task_name}' added to {pet_choice}!")

    # Show current tasks
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.markdown("**Current tasks:**")
        task_data = [
            {"Task": t.name, "Duration": f"{t.duration_minutes} min",
             "Priority": t.priority, "Time": t.time, "Frequency": t.frequency}
            for t in all_tasks
        ]
        st.table(task_data)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ── Step 3: Generate Plan ────────────────────────────────────────────────────
st.subheader("📅 Generate Daily Plan")

if st.session_state.owner is None:
    st.info("Set up your owner and pet above first.")
elif not st.session_state.owner.get_all_tasks():
    st.info("Add at least one task before generating a plan.")
else:
    if st.button("Generate schedule"):
        owner = st.session_state.owner
        scheduler = Scheduler(owner)

        # Show the plan
        plan = scheduler.generate_plan()
        if plan:
            st.success("Here's today's plan!")
            plan_data = [
                {"Task": t.name, "Time": t.time,
                 "Duration": f"{t.duration_minutes} min", "Priority": t.priority}
                for t in plan
            ]
            st.table(plan_data)
            st.markdown(f"**{scheduler.explain_plan()}**")
        else:
            st.warning("No tasks fit within your available time.")

        # Show conflicts
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.markdown("### ⚠️ Conflicts Detected")
            for c in conflicts:
                st.warning(c)
        else:
            st.success("✅ No scheduling conflicts!")