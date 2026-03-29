from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class Task:
    """A single pet care activity with scheduling constraints."""
    name: str
    duration_minutes: int
    priority: str          # "high", "medium", or "low"
    time: str              # Preferred time, format "HH:MM"
    frequency: str         # "daily", "weekly", or "once"
    is_complete: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_complete = True

    def reset(self):
        """Reset completion status (used for recurring tasks)."""
        self.is_complete = False


@dataclass
class Pet:
    """A pet belonging to an owner."""
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


@dataclass
class Owner:
    """The app user — manages pets and sets scheduling constraints."""
    name: str
    time_available_minutes: int
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's household."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """Generates and manages a daily care plan for all of an owner's pets."""

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority (high → medium → low)."""
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda t: self.PRIORITY_ORDER.get(t.priority, 99)
        )

    def sort_by_time(self) -> List[Task]:
        """Return tasks sorted chronologically by their time attribute."""
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda t: t.time
        )

    def filter_tasks(self, pet_name: Optional[str] = None, status: Optional[bool] = None) -> List[Task]:
        """Filter tasks by pet name and/or completion status."""
        results = []
        for pet in self.owner.pets:
            if pet_name and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.get_tasks():
                if status is not None and task.is_complete != status:
                    continue
                results.append(task)
        return results

    def detect_conflicts(self) -> List[str]:
        """Return warning strings for any tasks scheduled at the same time."""
        seen = {}
        warnings = []
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                if task.time in seen:
                    warnings.append(
                        f"⚠️ Conflict at {task.time}: '{task.name}' and '{seen[task.time]}' overlap!"
                    )
                else:
                    seen[task.time] = task.name
        return warnings

    def generate_plan(self) -> List[Task]:
        """Build a daily plan sorted by priority, fitting within time available."""
        sorted_tasks = self.sort_by_priority()
        plan = []
        total_time = 0
        for task in sorted_tasks:
            if total_time + task.duration_minutes <= self.owner.time_available_minutes:
                plan.append(task)
                total_time += task.duration_minutes
        return plan

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the generated plan."""
        plan = self.generate_plan()
        if not plan:
            return "No tasks fit within the available time."
        lines = ["📋 Today's Plan (sorted by priority):"]
        total = 0
        for task in plan:
            lines.append(f"  • [{task.priority.upper()}] {task.name} at {task.time} ({task.duration_minutes} min)")
            total += task.duration_minutes
        lines.append(f"\n⏱ Total time: {total} min of {self.owner.time_available_minutes} min available")
        return "\n".join(lines)

    def handle_recurrence(self, task: Task):
        """Reset a recurring task for the next occurrence."""
        if task.frequency in ("daily", "weekly"):
            task.reset()