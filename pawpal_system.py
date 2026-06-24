"""PawPal — pet task tracker.

Skeleton generated from diagrams/uml.mmd.
Fill in the method bodies to implement the system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PriorityLevel(Enum):
    """Priority of a task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    """A scheduled care task for a pet (e.g. walking, feeding)."""

    title: str
    priority: PriorityLevel
    scheduled_time: datetime
    duration: int
    completed: bool = False

    def notify_task(self) -> None:
        """Notify about this task at its scheduled time."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet profile and its tasks."""

    name: str
    type: str
    age: int
    care_needs: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task (e.g. walking, feeding) to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Delete / remove a task from this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """A pet owner who can add pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError
