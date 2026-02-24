# Context Management

Sources: Manus AI working memory patterns, obra/superpowers context methodology, production AI agent analysis

Covers: filesystem as working memory, the 2-Action Rule, file purposes, read vs write decisions, session recovery, context window optimization.

## The Core Pattern: Context Window as RAM vs Filesystem as Disk

The fundamental principle of AI agent planning is the separation of volatile working memory and persistent storage. An agent that relies solely on its conversation history will inevitably fail as the task complexity increases.

### The Entropy of Conversation
Every message exchanged between the user and the agent increases the "noise" in the context window. Information degrades over time through three primary mechanisms:
1. **Truncation**: As the window fills, the earliest parts of the conversation are discarded.
2. **Attention Dilution**: Large amounts of tool output (e.g., build logs, search results) distract the model from the core plan.
3. **Reasoning Drift**: Without a fixed source of truth, the agent's internal model of the task state subtly shifts with each new instruction.

### Context Window as RAM
The context window is your Random Access Memory (RAM). It is volatile, limited in size, and expensive in terms of both tokens and attention.
- Volatility: Information at the beginning of a long conversation is subject to "lost in the middle" phenomena and eventually gets truncated or compressed.
- Limited Capacity: Every token used for old tool outputs or redundant file reads reduces the space available for reasoning and new information.
- Shared Resource: The context window is a public good shared by the system prompt, user instructions, conversation history, and tool outputs. Treat it as a scarce resource.

### Filesystem as Disk
The filesystem is your Hard Disk Drive (HDD). it is persistent, virtually unlimited, and structured.
- Persistence: Data written to a file remains identical regardless of how many messages follow.
- State Recovery: Files allow an agent to "reboot" its context by reading a summary of the current state, bypassing thousands of lines of irrelevant history.
- Unlimited Scale: Complex projects require thousands of lines of research, code, and logs. These cannot fit in context but can easily fit in structured files.

Everything important must be moved from the "RAM" of the context window to the "Disk" of the filesystem immediately. If information exists only in the conversation history, it is effectively lost for long-term planning.

## Planning Files and Their Purposes

To maintain high fidelity over long sessions, use a specific set of planning files. Each serves a distinct purpose in the agent's cognitive architecture.

| File | Purpose | When to Update | What to Include | Storage Logic |
| :--- | :--- | :--- | :--- | :--- |
| `task_plan.md` | Primary source of truth and state machine. | After every phase completion, major error, or pivot. | Phases, high-level tasks, completion status, current decision, known blockers. | Append-only for history, overwrite for state. |
| `findings.md` | Repository for research, discovery, and patterns. | Immediately after finding key information via search or browser. | Code snippets, URL references, API schemas, architectural discoveries, answers to research questions. | Structured by topic or search query. |
| `progress.md` | Detailed log of implementation and session state. | After significant tool chains, test runs, or file modifications. | Specific files changed, test results (success/fail), shell commands run, current sub-task state. | Chronological log. |
| `decisions.md` | Permanent record of architectural and logical choices. | When choosing between multiple implementation paths. | Options considered, chosen path, rationale, rejected alternatives and why. | Decision log with timestamps. |
| `errors.md` | Tracking failed attempts to avoid repetition. | After a tool failure that requires a change in strategy. | Error message, command run, hypothesis on failure, the new approach taken. | List of "lessons learned". |

## The 2-Action Rule

The 2-Action Rule is a strict protocol designed to prevent information loss, particularly when dealing with multimodal or high-volume data.

### The Rule
After every 2 view, browser, or search operations, you MUST immediately save key findings to a text file.

### Rationale
- Multimodal Volatility: Screenshots, PDFs, and complex HTML layouts are extremely token-heavy. They provide high value when first viewed but are the first things to be dropped or ignored as the conversation continues.
- Working Memory Saturation: Human-like "short-term memory" for agents is roughly 2-3 complex operations. Beyond this, the details of the first operation begin to blur or vanish.
- Early Crystallization: Forcing yourself to write findings after 2 actions forces you to synthesize and crystallize knowledge while it is fresh.

### Implementation by Tool Type
- **Search Tools**: Perform 2 searches -> Write the list of promising URLs and snippets to `findings.md`.
- **Browser/Viewer**: Open 2 pages/images -> Write the key content or descriptions to `findings.md`.
- **File Exploration**: Run `ls` and `grep` -> Write the directory structure or key file paths found to `progress.md`.
- **Git Operations**: Run `status` and `diff` -> Write the staged/unstaged changes summary to `progress.md`.
- **Package Managers**: Run `install` and `list` -> Write the added dependencies to `findings.md`.

## Context Hygiene and Garbage Collection

Maintaining a clean context window is as important as writing to disk.

### Summarization
When a tool returns a large output (e.g., a 100-line error trace or a large JSON response), do not leave it raw in the context.
1. Extract the critical error message and the 5 lines of context.
2. Write the full output to a file (e.g., `logs/error_01.txt`).
3. Mention the file path and the summary in the conversation.

### Redundancy Removal
Never read the same file multiple times in a single turn. If you need to refer back to it, trust your memory of the first read or the summary you wrote to disk.

### Tool Output Management
If you run a build command that generates 200 lines of "Success" logs, do not repeat them. State "Build successful (200 lines of logs saved to .build_log)" and move on.

## Read vs Write Decision Matrix

Effective context management requires constant decisions about whether to ingest new data (Read) or persist current knowledge (Write).

| Situation | Action | Reason |
| :--- | :--- | :--- |
| Just wrote or edited a file. | DON'T read the file immediately. | The content you just wrote is still perfectly preserved in your recent context window. |
| Just viewed an image or PDF. | WRITE findings to `findings.md` immediately. | Visual and binary content does not persist well in textual conversation history. |
| Browser returned a large page. | WRITE relevant snippets to a file. | The full HTML is too noisy to keep in context. Extract the signal and discard the noise. |
| Starting a new major phase. | READ `task_plan.md` and `findings.md`. | Re-orient your internal state and clear any misconceptions from the previous phase. |
| An unexpected error occurred. | READ relevant source code and `progress.md`. | Ensure you have the absolute latest state before diagnosing the failure. |
| Resuming after a context reset. | READ ALL planning files (`task_plan`, `findings`, `progress`). | Full state recovery is only possible by loading the structured "Disk" state. |
| Context window feels saturated. | Summarize `progress.md` and write it to disk. | Move details out of the active window to make room for new reasoning. |
| Thinking about a complex refactor. | WRITE the proposed plan to `task_plan.md`. | Offload the complexity to disk before you start making changes that could confuse your memory. |
| Just finished a long research spike. | READ your own `findings.md`. | Consolidate everything you learned into a single coherent next step. |

## The 5-Question Reboot Test

Before making a major decision or starting a new phase, run this internal diagnostic. If you cannot answer these using only your active context and planning files, your context management has failed.

1. **Where am I?**
   Identify the specific phase and sub-task currently in progress as defined in `task_plan.md`.

2. **Where am I going?**
   Identify the next 2-3 steps required to complete the current phase.

3. **What is the goal?**
   Articulate the high-level objective and how the current sub-task contributes to it.

4. **What have I learned?**
   List the critical constraints, API requirements, or patterns discovered so far (stored in `findings.md`).

5. **What have I done?**
   Review the list of files modified and tests passed in the current session (stored in `progress.md`).

When to run:
- At the start of every session.
- After a long chain of tool outputs (more than 10 messages).
- Whenever you feel "lost" or are repeating yourself.

## Session Recovery Protocol

When context is lost due to a crash, a limit reach, or a break in the session, follow this protocol to resume work in under 3 minutes.

1. **Load Current State**: Read `task_plan.md`. Identify the last marked "in_progress" task.
2. **Load Recent History**: Read `progress.md`. Understand exactly what happened in the last 15-20 minutes of the previous session.
3. **Load Knowledge Base**: Read `findings.md`. Ensure you don't waste time re-searching for information you already found.
4. **Validate State**: Run a quick directory listing or check `git status` to verify the physical files match your `progress.md` log.
5. **Re-orient**: Run the 5-Question Reboot Test.
6. **Update and Continue**: If the plan is stale, update it. Otherwise, immediately begin the next sub-task.

## Context Window Optimization

Every message you send and receive has a token cost. Manage your "token budget" aggressively.

### Minimize Input Noise
- Do not read entire large files if you only need a specific function. Use `grep` or specific line-range reads.
- If a tool returns a massive amount of data, summarize it immediately and use the summary in your reasoning.
- Clear the conversation history (if the platform allows) or trigger a summarization event when the window is 70% full.

### Structure Output for Efficiency
- Use `TodoWrite` for high-level task tracking. It is lightweight and often persists in a special area of the agent's interface.
- Use planning files on disk for high-detail information.
- Avoid repeating your entire plan in every message. Refer to `task_plan.md` by name.

### Token Awareness
- System Prompt: Fixed cost.
- Conversation History: Growing cost.
- Planning Files: On-demand cost (only pay when you read).
- Tool Output: Variable cost.

Strategy: Keep the conversation history lean by moving details to files. A 50-line `task_plan.md` is far more valuable than 500 lines of chat history.

## Information Lifecycle

Manage information based on how long it needs to remain accessible.

| Information Type | Lifespan | Storage Location | Processing Strategy |
| :--- | :--- | :--- | :--- |
| Tool Output / Errors | Immediate | Context -> Discarded. | Extract 5% signal, ignore 95% noise. |
| Current Task State | Session | `TodoWrite` + active window. | Updated via tool calls. |
| Research / Patterns | Persistent | `findings.md` on disk. | Append-only until phase completion. |
| Architecture / Decisions | Persistent | `decisions.md` on disk. | Overwrite with latest reasoning. |
| High-level Roadmap | Persistent | `task_plan.md` on disk. | Constant state updates. |
| Project History | Archival | Git history / commits. | Documented in commit messages. |

## File Location Rules

Proper organization ensures that planning files do not clutter the codebase and are easily discoverable.

| Location | Content | Governance |
| :--- | :--- | :--- |
| Project Root | `task_plan.md`, `findings.md`, `progress.md`. | Agent-controlled. |
| `.sisyphus/` or `.planning/` | Hidden planning directories for large-scale projects. | Shared/Shared. |
| Skill Directory | Read-only templates and reference files. | Read-only. |
| `/tmp/` | Extremely large, temporary data dumps. | Auto-deleted. |

## Managing Different Data Types

Different types of information require different persistence strategies to remain useful.

### Quantitative Data
When dealing with numbers, benchmarks, or performance metrics, always use a table in a dedicated file. Do not rely on "about" or "approximately" in conversation.
- Example: Write build times to `performance_log.md`.

### Structural Data
Directory trees, dependency graphs, and architecture diagrams should be stored as ASCII or Mermaid in `findings.md`.
- Example: Write the result of `tree -L 3` to `findings.md`.

### Qualitative Data
User preferences, design critiques, and stylistic choices should be recorded in `decisions.md` with the exact quote or context from the user.

## Multi-Agent Handoffs and Persistence

In environments where different agents may work on the same task sequentially, context management becomes the protocol for "handoff".

1. **State Injection**: The incoming agent's first action should be reading the planning files.
2. **Context Packaging**: The outgoing agent should ensure that all "RAM" state is flushed to "Disk" before ending their turn.
3. **Consistency Verification**: Incoming agents must verify that the state in `task_plan.md` matches the actual state of the filesystem.

## Anti-Patterns

Avoid these common context management failures:

1. **Using TodoWrite for persistence**
   - DON'T: Rely solely on the Todo tool for long-term project state. It is volatile and may be cleared.
   - DO: Use `task_plan.md` as the definitive source of truth.

2. **Stating goals once and forgetting**
   - DON'T: Assume you will remember the primary goal after 50 messages.
   - DO: Re-read the goal statement in `task_plan.md` before every major decision.

3. **Hiding errors and retrying silently**
   - DON'T: Try the same failed command 3 times without recording the error.
   - DO: Log the specific error message to `progress.md` or `task_plan.md` before pivoting.

4. **Stuffing everything in context**
   - DON'T: Read five 500-line files into the conversation at once.
   - DO: Store the contents on disk and read only the sections you are currently editing.

5. **Starting execution immediately**
   - DON'T: Begin running `npm install` or `mkdir` before a plan exists.
   - DO: Create and save `task_plan.md` as the very first action.

6. **Repeating failed actions**
   - DON'T: Re-run a search because you forgot the results.
   - DO: Refer to `findings.md` for previously discovered data.

7. **Creating files in the skill directory**
   - DON'T: Write your project logs into the folder where the agent's logic lives.
   - DO: Create all planning files in the project root of the user's workspace.

8. **Redundant Reading**
   - DON'T: Call the Read tool on a file you just modified with the Edit tool.
   - DO: Trust your internal representation of the change you just made.

9. **The "Hope-Based" Search**
   - DON'T: Search for something, find nothing, and search again with a slightly different keyword without recording the failure.
   - DO: Log "Search for X yielded no results" in `findings.md` to prune the search tree.

10. **The Context Flush Blindness**
    - DON'T: Delete or ignore large tool outputs that contained vital information.
    - DO: Summarize the output into `findings.md` BEFORE it is rotated out of the active window.

11. **Shadow State Management**
    - DON'T: Keep "mental notes" about variable names or file paths.
    - DO: Write every "mental note" into `progress.md` immediately.

12. **The Endless Scroll**
    - DON'T: Keep scrolling through browser history to find a URL you saw 10 minutes ago.
    - DO: Extract the URL to `findings.md` as soon as you see it.

13. **Blind Resume**
    - DON'T: Start working on a task from memory after a 10-minute pause.
    - DO: Re-read the last 3 entries in `progress.md` to re-sync your state.

14. **Silent Pivots**
    - DON'T: Change your implementation strategy because of an error without updating the plan.
    - DO: Update `task_plan.md` with the "Pivoted to X because of Y" reasoning.

15. **Over-Reading**
    - DON'T: Read a file to "check if it's there".
    - DO: Use `ls` or `stat` to check existence; only read when you need content.
