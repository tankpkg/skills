# AI Planning Patterns

Sources: ReAct (Yao et al., 2023), Tree-of-Thoughts (Yao et al., 2023), Plan-and-Solve (Wang et al., 2023), LangGraph, BabyAGI

Covers: ReAct reasoning loop, chain-of-thought planning, tree-of-thoughts exploration, plan-and-solve separation, dynamic task generation, pattern selection.

## 1. ReAct (Reasoning + Acting)

ReAct integrates reasoning traces and task-specific actions in an interleaved manner. This pattern allows the agent to reason about the current state, determine which tool to use, and adjust its plan based on real-world feedback (observations).

### Core Loop: Thought, Action, Observation

1. Thought: Express reasoning about the current state. Identify what information is missing and justify the next step. High-quality thoughts prevent "tool-calling spam" by verifying preconditions before execution.
2. Action: Call a specific tool or API (e.g., search, read_file, execute_command).
3. Observation: Process the raw output returned by the action. This is the "grounding" phase where the agent connects its internal model to external reality.
4. Repeat: Use the observation to inform the next Thought. If the observation contradicts the previous Thought, the agent must update its mental model.

### ReAct Pseudocode

```python
def react_loop(task):
    history = []
    while not task.is_complete():
        # Step 1: Reason about the state
        thought = model.generate_thought(task, history)
        
        # Step 2: Extract and execute tool call
        action = model.parse_action(thought)
        observation = environment.execute(action)
        
        # Step 3: Record the loop interaction
        history.append({
            "thought": thought,
            "action": action,
            "observation": observation
        })
        
        # Step 4: Check for termination
        if "Final Answer" in thought or task.check_completion(observation):
            return thought
```

### When to Use
- Tasks requiring external information: When the model's weights don't contain the specific data (e.g., current file contents).
- Multi-step tool use: When the parameters of step N depend on the output of step N-1.
- Error-prone environments: When actions might fail and require immediate correction.

### When NOT to Use
- Simple deterministic tasks: Where a single script or direct command is sufficient.
- Reasoning-only tasks: Where the answer can be derived without external data.

## 2. Chain-of-Thought (CoT) Planning

Chain-of-Thought encourages the model to generate intermediate reasoning steps that lead to the final answer. In a planning context, this involves decomposing a complex goal into logical sub-tasks before attempting any execution.

### Key Variants
- Zero-shot CoT: Triggered by instructions like "Think step-by-step." This forces the model to allocate more compute (tokens) to reasoning.
- Self-Consistency: Generate multiple reasoning paths (e.g., 5 different CoT traces). Select the most frequent final answer. This is particularly effective for mathematical or highly structured logical problems.
- Chain-of-Verification (CoVe): After generating a CoT, the model generates "verification questions" to check its own reasoning for hallucinations.

### Practical Application: The "Pre-Execution Pass"
Before executing a change, perform a CoT reasoning pass:
"The user wants to rename the 'User' class to 'Account'. Let me think through the implications. First, I need to find all imports in the 'src/' directory. Second, I need to check the database schema in 'models/'. Third, I must verify if any external APIs depend on this class name. Fourth, I must update the tests. Only then can I start the rename."

### Limitations
- Verbosity: High token consumption can be wasteful for trivial tasks.
- Error Compounding: A logical error in the first reasoning step cascades through all subsequent steps without the "grounding" check that ReAct provides.

## 3. Tree-of-Thoughts (ToT)

Tree-of-Thoughts enables the exploration of multiple reasoning branches. Unlike CoT, which follows a linear path, ToT treats the problem as a search over a tree where each node is a "thought" representing a partial solution.

### ToT Process
1. Thought Generation: Generate multiple candidate next steps (e.g., 3-5 potential approaches) for the current state.
2. State Evaluation: Score each candidate (e.g., 0 to 1, or "valid/invalid/possible") based on its likelihood of leading to a solution.
3. Search Algorithm: Use Breadth-First Search (BFS) or Depth-First Search (DFS) to navigate the tree.
4. Pruning: Discard low-scoring branches immediately. This is the "Look-ahead" capability that distinguishes ToT from basic CoT.

### ToT Pseudocode

```python
def tree_of_thoughts(initial_state, n_candidates=3):
    queue = [initial_state]
    while queue:
        state = queue.pop(0)
        # Generate N candidate next-thoughts
        candidates = model.generate_candidates(state, n=n_candidates)
        
        for c in candidates:
            # Heuristic evaluation of the candidate
            score = model.evaluate(c) 
            
            if score > threshold:
                if c.is_goal(): 
                    return c.reconstruct_path()
                queue.append(c)
        
        # Sort queue to prioritize promising branches
        queue.sort(key=lambda x: x.score, reverse=True)
```

### When to Use
- Architecture Decisions: Evaluating multiple design patterns or tech stacks.
- Creative Problem Solving: When there are multiple ways to implement a feature, each with different trade-offs.
- Navigating Large State Spaces: When the first few steps are non-obvious.

### When NOT to Use
- Linear Tasks: When the sequence of steps is well-known and deterministic.
- Resource-Constrained Sessions: ToT is significantly more expensive than linear patterns.

## 4. Plan-and-Solve

Plan-and-Solve separates the planning effort from the execution effort. This pattern is highly efficient for well-defined tasks and reduces the "reasoning overhead" during the execution phase.

### Execution Phases
- Phase 1 (Plan): Use a high-capability model (e.g., Gemini 1.5 Pro) to generate a comprehensive, ordered list of tasks required to achieve the goal.
- Phase 2 (Solve): Execute the tasks one by one. The executor model can often be a smaller, faster model (e.g., Gemini 1.5 Flash) because the "hard reasoning" was already completed in Phase 1.

### Specialized Variants
- ReWOO (Reasoning Without Observation): The planner generates a plan with specific "evidence slots" (e.g., E1, E2). The executor fills these slots by calling tools. The final response is generated by a "Solver" that sees all evidence at once.
- LLMCompiler: Generates a directed acyclic graph (DAG) of tasks. It identifies which tasks can be run in parallel (no dependencies) and which must wait for previous outputs. This drastically reduces execution time in multi-tool scenarios.

### Plan-and-Solve Pseudocode

```python
def plan_and_solve(goal):
    # Phase 1: Planning
    plan = planner_model.generate_full_plan(goal)
    
    # Phase 2: Sequential Execution
    context = []
    for step in plan.steps:
        # Each step inherits context from previous results
        result = executor_model.execute(step, context=context)
        context.append({"step": step.id, "result": result})
    
    return context
```

## 5. Dynamic Task Generation (BabyAGI Pattern)

The Dynamic Task Generation pattern treats the plan as a living document. It is designed for exploratory tasks where the full scope cannot be known until the first few steps are completed.

### Core Mechanism
1. Execution: Perform the top task in the priority queue.
2. Result Analysis: Analyze the output of the task to determine if the objective was met or if more work is needed.
3. Task Creation: Generate new tasks based on findings. For example, a successful file read might suggest three new files to search.
4. Prioritization: Re-order the task queue based on the new total state. Ensure that the most critical "blocker" tasks are moved to the top.

### Practical Example: Complex Bug Investigation
- Task 1: Check application logs for stack traces.
- Finding: "Database connection timeout in module X."
- Dynamic Update:
    - New Task 2: Check database service status (Priority: 1).
    - New Task 3: Check network latency between app and DB (Priority: 2).
    - New Task 4: Audit module X for connection leaks (Priority: 3).
- Execution: Proceed to Task 2.

## 6. Iterative Refinement

Iterative refinement focuses on improving an initial output through successive cycles of evaluation and modification.

### Refinement Loop
1. Draft: Generate an initial solution (e.g., a "naive" implementation of an algorithm).
2. Critique: Perform a self-critique or run automated tools. Ask: "Where will this fail?", "Is this efficient?", "Does this follow the style guide?".
3. Refine: Update the code or plan based on the critique.
4. Repeat: Continue for a fixed number of rounds or until the critique returns "No issues found."

### Refinement Criteria
- Correctness: Does it solve all aspects of the user's request?
- Robustness: Are edge cases (nulls, empty strings, large inputs) handled?
- Performance: Is the Big-O complexity acceptable for the use case?
- Style: Does it match the existing patterns in the codebase?

## 7. Pattern Selection Decision Tree

Select the planning pattern based on the nature of the task and the environment.

### Selection Table

| Situation | Best Pattern | Why |
|-----------|--------------|-----|
| External data needed (APIs, Files) | ReAct | Interleaves observation with reasoning to ground actions. |
| Multiple valid architectural paths | Tree-of-Thoughts | Explicitly branches and compares alternatives. |
| Known scope, well-defined steps | Plan-and-Solve | Maximizes efficiency by minimizing reasoning loops. |
| Pure logic, no tool use needed | Chain-of-Thought | Allocates more tokens to the reasoning process. |
| Exploratory research, unknown scope | Dynamic Tasks | Recalculates the task list after every discovery. |
| Improving existing code/drafts | Iterative Refinement | Focuses on incremental quality and bug-finding. |

### ASCII Decision Tree

```
Start Task Investigation
  |
  +-- Need external information? -- [Yes] --> ReAct
  |     |
  |    [No]
  |     v
  +-- Multiple valid solutions? -- [Yes] --> Tree-of-Thoughts
  |     |
  |    [No]
  |     v
  +-- Scope fully known? --------- [Yes] --> Plan-and-Solve
  |     |
  |    [No]
  |     v
  +-- Exploratory in nature? ----- [Yes] --> Dynamic Task Generation
        |
       [No]
        v
    Chain-of-Thought
```

## 8. Combining Patterns

In production-grade agents, these patterns are often hybridized to handle complex, multi-modal tasks.

| Combination | When to Use | Example |
|-------------|-------------|---------|
| CoT + ReAct | High-level reasoning before acting. | Analyze the bug report (CoT), then start searching (ReAct). |
| ToT + Plan-and-Solve | Comparing plans before execution. | Brainstorm 3 implementation plans (ToT), pick one, execute (P&S). |
| ReAct + Dynamic Tasks | Adapting to environment discovery. | Search for a component (ReAct), then add new tasks based on what you found. |
| CoT + Iterative Refinement | Complex logic generation. | Reason through the algorithm (CoT), then refine the code for speed. |

## 9. Practical Application for Coding Agents

Concrete mappings between developer tasks and planning patterns:

| Scenario | Pattern | First Step |
|----------|---------|------------|
| Implementing a new feature | Plan-and-Solve | Generate a step-by-step implementation guide. |
| Investigating a production bug | ReAct | Use grep to find the error message in the logs. |
| Choosing a new library/package | Tree-of-Thoughts | List 3 candidates and evaluate their GitHub metrics. |
| Refactoring a legacy module | Iterative Refinement | Run existing tests to establish a baseline. |
| Writing a complex SQL query | Chain-of-Thought | Break the JOIN logic into a step-by-step reasoning list. |
| Performing a security audit | Dynamic Tasks | Check one entry point, then add tasks for found vulnerabilities. |

## 10. AI Planning Anti-Patterns

- Hallucinated Tools: Including actions in a plan for tools or methods that do not exist in the environment.
- Infinite Reasoning Loops: Generating endless "Thoughts" without ever committing to an "Action." This often happens when the agent is "scared" to fail.
- Brittle Execution: Using Plan-and-Solve for tasks where the environment is highly unpredictable. The plan fails at step 2, but the agent blindly attempts step 3.
- Majority Vote of Errors: In Self-Consistency CoT, assuming the most frequent answer is correct when the logic itself is flawed across all generated paths.
- Combinatorial Explosion: Using Tree-of-Thoughts without aggressive pruning, leading to massive token costs and context window overflow.
- Goal Drift: In Dynamic Task Generation, allowing sub-tasks to lead the agent into a "rabbit hole" that is irrelevant to the original user intent.
- Blind Refinement: Repeating the Iterative Refinement loop without new information or actual test results, leading to "over-polishing" that often introduces regressions.
- Static Planning in Dynamic Repos: Creating a full 10-step plan but failing to update it when step 1 (a file search) reveals the codebase structure is completely different than expected.
- Over-Planning: Spending 5 minutes generating a Tree-of-Thoughts for a task that could have been solved with a single `grep` command.
- Observation Neglect: In ReAct, when the agent ignores a "File not found" observation and continues to reason as if the file was read successfully.
- Logic Leaps: In CoT, jumping from "Step 1: Read file" to "Step 10: Bug fixed" without explaining the intermediate transformations.
- Execution Stalling: When an agent uses Dynamic Task Generation to keep adding "Analyze X" tasks instead of ever performing a "Write Y" task.
