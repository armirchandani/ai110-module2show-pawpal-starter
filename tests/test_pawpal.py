import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# --- Fixtures ---
def make_scheduler():
    owner = Owner(name="Aastha", time_available_minutes=120)
    dog = Pet(name="Max", species="Dog")
    dog.add_task(Task(name="Walk", duration_minutes=30, priority="high", time="07:00", frequency="daily"))
    dog.add_task(Task(name="Feeding", duration_minutes=10, priority="high", time="08:00", frequency="daily"))
    dog.add_task(Task(name="Grooming", duration_minutes=20, priority="low", time="10:00", frequency="weekly"))
    owner.add_pet(dog)
    return Scheduler(owner)


# --- Test 1: Task completion ---
def test_mark_complete():
    task = Task(name="Walk", duration_minutes=30, priority="high", time="07:00", frequency="daily")
    assert task.is_complete == False
    task.mark_complete()
    assert task.is_complete == True


# --- Test 2: Adding a task increases pet task count ---
def test_add_task_increases_count():
    pet = Pet(name="Max", species="Dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(name="Walk", duration_minutes=30, priority="high", time="07:00", frequency="daily"))
    assert len(pet.get_tasks()) == 1


# --- Test 3: Tasks are sorted chronologically ---
def test_sort_by_time():
    scheduler = make_scheduler()
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times)


# --- Test 4: Conflict detection ---
def test_detect_conflicts():
    owner = Owner(name="Aastha", time_available_minutes=120)
    dog = Pet(name="Max", species="Dog")
    dog.add_task(Task(name="Walk", duration_minutes=30, priority="high", time="08:00", frequency="daily"))
    dog.add_task(Task(name="Feeding", duration_minutes=10, priority="high", time="08:00", frequency="daily"))
    owner.add_pet(dog)
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) > 0


# --- Test 5: Plan respects time available ---
def test_generate_plan_respects_time():
    owner = Owner(name="Aastha", time_available_minutes=30)
    dog = Pet(name="Max", species="Dog")
    dog.add_task(Task(name="Walk", duration_minutes=30, priority="high", time="07:00", frequency="daily"))
    dog.add_task(Task(name="Grooming", duration_minutes=60, priority="low", time="10:00", frequency="weekly"))
    owner.add_pet(dog)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    total = sum(t.duration_minutes for t in plan)
    assert total <= 30