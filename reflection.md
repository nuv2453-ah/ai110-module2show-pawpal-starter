PawPal+ Project Reflection
1. System Design

a. Initial design

For PawPal+, I initially designed four main classes to model the system: Owner, Pet, Task, and Scheduler. These classes capture the core objects and responsibilities of the pet care management system.

Core user actions

Add a new pet to their profile.
Schedules tasks for pets (walks, feedings, medications, vet appointments).
Views and manages today’s tasks, including marking tasks as done.

Classes and Responsibilities

Owner
Attributes: name, email, pets (list of Pet objects)
Methods:
add_pet(pet): Add a pet to the owner’s profile.
remove_pet(pet): Remove a pet from the owner.
get_all_tasks(): Retrieve all tasks across all pets.
Pet Attributes: name, species, age, tasks (list of Task objects)
Methods:
add_task(task): Assign a task to the pet.
remove_task(task): Remove a task from the pet.
Task
Attributes: task_type, time, priority, recurrence, done
Methods:
mark_done(): Mark the task as completed.
is_conflict_with(other_task): Check if two tasks overlap in time.
get_occurrence_for_date(target_date): Return a task occurrence for a specific date, accounting for recurrence.
Scheduler
Attributes: task_list (all tasks across pets)
Methods:
load_tasks_from_owner(owner): Load tasks from an owner’s pets.
sort_tasks(): Sort tasks by time, then by priority.
detect_conflicts(): Identify conflicting tasks (tasks at the same time).
get_today_tasks(): Retrieve tasks scheduled for today.
complete_task(task): Mark a task complete and handle recurrence.
filter_by_status(done): Filter tasks by completion status.

b. Design changes

During implementation, I refined how recurring tasks were handled. Initially, I considered storing all occurrences explicitly, but this would have required duplicating tasks for future dates. Instead, I implemented a dynamic recurrence system in get_occurrence_for_date() and complete_task(), which generates the next occurrence only when a task is completed. This reduces memory usage and makes scheduling more flexible.

2. Scheduling Logic and Tradeoffs

a. Constraints and priorities

The scheduler considers the following constraints:

Time: Tasks are ordered chronologically.
Priority: Higher priority tasks appear first if times are equal.
Recurrence: Daily and weekly tasks automatically reappear after completion.
Conflict avoidance: Tasks with identical timestamps are flagged.

I prioritized time first, because a pet owner needs a clear chronological plan, and priority second to ensure urgent tasks are emphasized.

b. Tradeoffs

The scheduler only checks for exact time matches to detect conflicts, rather than overlapping durations. This simplifies the algorithm and is reasonable for this scenario because PawPal+ tasks are short, discrete events (walks, feedings, medications), so exact-time conflicts capture the majority of scheduling issues without overcomplicating the logic.

3. AI Collaboration

a. How I used AI

AI was used for:

Brainstorming UML diagrams and validating class relationships.
Generating initial Python class skeletons with dataclasses.
Suggesting algorithms for sorting, filtering, recurrence handling, and conflict detection.
Drafting automated test functions to cover edge cases.

Prompts that worked best included asking AI to translate UML into Python classes, implement recurrence logic with timedelta, and generate pytest test cases.

b. Judgment and verification

I did not accept AI suggestions blindly. For example, AI initially suggested a recurrence system that created all future occurrences at once, which could overwhelm memory for long-term schedules. I evaluated this by reasoning about task volume and verifying with small tests, then implemented a dynamic generation approach instead.

4. Testing and Verification

a. What you tested

Task completion: mark_done() correctly updates task status.
Task addition/removal: Pets correctly store their tasks.
Sorting correctness: Tasks are returned in chronological order, with priority as a tie-breaker.
Recurrence logic: Daily and weekly tasks generate a new occurrence after completion.
Conflict detection: Scheduler flags tasks with the same timestamp.
Edge cases: Pets with no tasks, no conflicts, and filtering tasks by completion status.

These tests were crucial to ensure the scheduler produced accurate daily plans, correctly handled recurring tasks, and flagged conflicts.

b. Confidence

I am confident the scheduler works correctly for the tested scenarios. If I had more time, I would test:

Overlapping durations: Tasks that span multiple hours.
Time zone changes or DST adjustments.
Simultaneous recurrence across multiple pets.

5. Reflection

a. What went well

I am most satisfied with the dynamic recurrence system and conflict detection, which allow PawPal+ to handle daily and weekly tasks intuitively while keeping the scheduler lightweight and efficient. The CLI-first workflow helped me validate all logic before integrating with Streamlit.

b. What you would improve

Next iteration, I would redesign the scheduler to handle task durations, allowing it to detect overlapping tasks more realistically. I would also add user preferences for task order (e.g., morning vs. evening) to improve the daily plan’s usability.

c. Key takeaway

The most important lesson was that AI is a powerful collaborator, but human judgment is essential. I learned to use AI to accelerate brainstorming, scaffolding, and testing while verifying that the resulting logic aligns with real-world constraints and user needs. 
