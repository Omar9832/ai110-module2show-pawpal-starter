# PawPal+ Project Reflection

## 1. System Design


The main goal of PawPal+ is to support pet owners in organizing and completing daily care tasks. The three core actions a user should be able to perform are:

1. Add/manage a pet profile — The user can add information about their pet, such as name, type, age, and care needs.

2. Create and receive reminders for care tasks — The user can schedule tasks like feeding, walks, medication, or grooming and receive notifications when they need to be done.

3. View and complete daily tasks — The user can view their planned schedule and mark tasks as completed after completing them.

**a. Initial design**

- Briefly describe your initial UML design.
    
    My initial UML design is composed of four main components: Owner, Pet, Task, and PriorityLevel. Each class has a specific role and represents an important part of the PawPal+ system. The Owner class represents the user and manages the pets associated with them. The Pet class stores information about the pet and is connected to the care tasks that need to be completed. The Task class represents individual pet care activities, while PriorityLevel helps categorize tasks based on their importance. The relationships between these classes allow an owner to manage pets, assign tasks, and track completed care activities.

What classes did you include, and what responsibilities did you assign to each?
    
    The classes I included are Owner, Pet, Task, and PriorityLevel. The Owner class is responsible for storing owner information and managing pet profiles by allowing the user to add pets. The Pet class stores details about the pet, such as its name, type, age, and care needs, and it manages the tasks assigned to that pet. The Task class represents individual care activities and stores information such as the task name, priority level, duration, scheduled time, and completion status. It is also responsible for task-related actions such as notifications and tracking completion. The PriorityLevel class is responsible for defining the importance of tasks so the scheduler can determine which tasks should be prioritized.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

    Yes, my design changed during implementation. I made three notable changes:

    First, I had originally placed the add_pet() method inside the Pet class, but this did not accurately represent the relationship between the objects because a pet should not be responsible for adding other pets. I moved add_pet() from the Pet class to the Owner class, since the owner is the user who actually manages and adds pets to the system.

    Second, I had initially given the Task class responsibility for creating and removing tasks (create_task() and remove_task()). This was backwards: a single task should not manage the collection of tasks it belongs to. I moved that responsibility to the Pet class as add_task() and remove_task(), because a pet "has many" tasks and is the natural owner of that list.

    Third, while implementing remove_task() I realized that comparing tasks by their fields was unsafe. Because Task is a dataclass, two tasks with the same title, priority, scheduled time, and duration (for example a morning walk and an evening walk that look identical) would be treated as equal, so removing one could delete the wrong one. I added a unique id field to Task so each task is distinct, and changed remove_task() to match on that id. This removed the duplicate-task ambiguity and made deletion reliable.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
