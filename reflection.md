# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
For PawPal+, I designed four main classes.

**Core user actions**
1. Add a new pet to their profile.
2. Schedule a task for a pet (walk, feeding, medication, vet appointment).
3. View and manage today's tasks, including marking tasks as done.

### Classes

1. **Owner**
   - **Attributes**
     - `name`: string
     - `email`: string
     - `pets`: list of Pet objects
   - **Methods / Responsibilities**
     - `add_pet(pet)`: adds a new pet to the owner
     - `remove_pet(pet)`: removes a pet from the owner

2. **Pet**
   - **Attributes**
     - `name`: string
     - `species`: string
     - `age`: integer
     - `tasks`: list of Task objects
   - **Methods / Responsibilities**
     - `add_task(task)`: adds a new task to the pet
     - `remove_task(task)`: removes a task from the pet

3. **Task**
   - **Attributes**
     - `task_type`: string (walk, feed, medication)
     - `time`: datetime
     - `priority`: integer
     - `recurrence`: string or None
     - `done`: boolean
   - **Methods / Responsibilities**
     - `mark_done()`: marks the task as completed
     - `is_conflict_with(other_task)`: checks if this task conflicts with another

4. **Scheduler**
   - **Attributes**
     - `task_list`: list of all tasks across pets
   - **Methods / Responsibilities**
     - `sort_tasks()`: sorts tasks by time or priority
     - `detect_conflicts()`: finds conflicting tasks
     - `get_today_tasks()`: returns tasks scheduled for today

- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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
