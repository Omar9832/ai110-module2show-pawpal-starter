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

    My scheduler organizes tasks according to their scheduled time and priority level. Tasks are shown first if they occur earlier in the day. Higher-priority tasks are listed before lower-priority ones. It also excludes completed tasks from the upcoming schedule and tasks are able to be filtered by pet name or completion status. I selected these constraints since completing pet care tasks on time is the most important goal. On the other hand, priority helps determine which task should be completed first when there is a scheduling conflict.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

    One tradeoff my scheduler provides is using a simple conflict detection algorithm that makes a comparasion between tasks to identify overlapping time ranges. While more advanced algorithms could enhance performance for very large schedules, they would also make the code challenging to understand and maintain. Because this application is designed to manage a relatively small amount of pet care tasks, the more practical approach is an appropriate balance between readability and functionality.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

    I used AI at a few points rather than all at once. At the start I mostly used it to brainstorm, because I wanted to know what edge cases a scheduler with sorting and recurring tasks should handle, and that's where the idea of two tasks starting at the same time came from. Once the classes were working I leaned on it more for the tedious parts, like drafting test functions for sorting, recurrence, and conflicts, and rewriting the Streamlit display so it used my Scheduler methods and showed things in tables instead of plain text. I also had it help me update the UML diagram after my design changed, mostly because I kept forgetting to keep it in sync.

    The prompts that worked best were the specific ones. If I pointed it at the actual file and asked something concrete, I usually got back something I could use and check. When I was vague, the answers were vague too. Telling it what I already had and what I wanted next was really what made the difference.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

    The clearest example was a test the AI wrote for conflict detection. It compared the two clashing tasks by putting them into a set, which looked reasonable enough that I almost left it alone. When I ran pytest it failed, because my Task is a mutable dataclass and Python won't let you put those in a set. I changed it to just check that both tasks were in the returned pair, and then it passed. That one stuck with me because the code looked right and still didn't work.

    After that I made a point of running things instead of assuming they were fine. I ran the test suite whenever I added tests, ran main.py to check the CLI output actually matched what the README claimed, and went through the UML class by class against my code. When the AI told me my old diagram was out of date, I didn't just take its word for it, I went and checked each class myself first.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

    I focused my tests on the core behaviors. I checked that marking a task complete changes its status, that adding a task to a pet increases the task count, that sorting returns tasks in time order, that completing a daily task creates a copy for the next day, and that two tasks at the same time get flagged as a conflict.

    I picked these because they're basically the things the app promises to do. If the sorting is off, the whole daily plan is useless. If recurrence doesn't carry a task forward, a repeating task just quietly disappears. And if conflicts aren't caught, the owner ends up double-booked with no warning. The completion and add-task tests are more basic, but everything else is built on top of them, so I wanted those covered too.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

    I'm reasonably confident. All five tests pass and they hit the features I care about most, so I trust it in the normal cases. What I'm less sure about is the edge behavior my tests don't reach yet.

    If I had more time, the first thing I'd add is the case where one task ends exactly when the next one starts, like 8:00 to 8:30 and then something at 8:30, since that shouldn't count as a conflict and I'd want to be sure it doesn't. I'd also test weekly recurrence the same way I did daily, try three tasks overlapping at once, check that the priority tie-break works when two tasks share a time, and run through the different filter combinations. Testing an empty schedule with no pets or tasks would be worth doing as well, just so I know nothing breaks on the empty case.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

    I'm most proud of how much cleaner the design got as I actually built it. Moving add_pet() onto the Owner and add_task()/remove_task() onto the Pet made each class own the right thing, and it stopped feeling awkward. Adding the id field to Task fixed a genuine bug too, where two tasks that looked identical could get mixed up when I tried to remove one. And I like that the Scheduler stayed separate from the data classes. It just reads the pets from the Owner and does all the sorting and conflict work in one place, which made the whole thing a lot easier to follow.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

    The main thing is that nothing gets saved. Everything lives in memory right now, so the moment the app restarts, all the pets and tasks are gone. Adding real storage so it persists between sessions would make it feel like an actual product. I'd also want users to be able to edit or delete tasks from the UI instead of only adding and completing them, and I'd make the schedule handle more than one day instead of assuming everything is today. Turning the printed reminders into real notifications would be a nice follow-up as well.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

    What stuck with me most is that figuring out which class is responsible for what matters more than the code you end up writing. Once the responsibilities were right, with the owner handling pets and the pet handling its own tasks, the actual implementation kind of fell into place. With AI, the lesson was that it's fast and useful for drafts and refactors, but I can't take the output at face value. Running the tests and the app myself was what actually told me whether something worked, and once or twice that was the only reason I noticed a problem at all.
