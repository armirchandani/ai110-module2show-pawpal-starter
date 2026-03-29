from pawpal_system import Task, Pet, Owner, Scheduler

# --- Create Owner ---
owner = Owner(name="Aastha", time_available_minutes=120)

# --- Create Pets ---
dog = Pet(name="Max", species="Dog")
cat = Pet(name="Luna", species="Cat")

# --- Add Tasks to Dog ---
dog.add_task(Task(name="Morning Walk", duration_minutes=30, priority="high", time="07:00", frequency="daily"))
dog.add_task(Task(name="Feeding", duration_minutes=10, priority="high", time="08:00", frequency="daily"))
dog.add_task(Task(name="Grooming", duration_minutes=20, priority="low", time="10:00", frequency="weekly"))

# --- Add Tasks to Cat ---
cat.add_task(Task(name="Feeding", duration_minutes=10, priority="high", time="08:00", frequency="daily"))
cat.add_task(Task(name="Playtime", duration_minutes=15, priority="medium", time="17:00", frequency="daily"))

# --- Add Pets to Owner ---
owner.add_pet(dog)
owner.add_pet(cat)

# --- Create Scheduler ---
scheduler = Scheduler(owner)

# --- Print Daily Plan ---
print(scheduler.explain_plan())

# --- Print Conflicts ---
print("\n🔍 Conflict Check:")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        print(c)
else:
    print("  No conflicts found.")

# --- Print Sorted by Time ---
print("\n🕐 All Tasks Sorted by Time:")
for task in scheduler.sort_by_time():
    print(f"  {task.time} — {task.name} ({task.priority})")