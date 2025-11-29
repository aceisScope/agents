# Agentic Design Patterns Analysis - Lab 2

## Agentic Design Patterns Used

### 1. **Parallelization Pattern**
- **Location**: Cell 10 (lines 318-328)
- **Pattern**: Code breaks task into parallel pieces, sends to multiple LLMs simultaneously
- **Implementation**: `asyncio.gather()` runs three sales agents in parallel
- **Code**:
```python
results = await asyncio.gather(
    Runner.run(sales_agent1, message),
    Runner.run(sales_agent2, message),
    Runner.run(sales_agent3, message),
)
```
- **Key**: Code orchestrates, not the LLM; concurrent execution for efficiency

### 2. **Evaluator-Optimizer Pattern**
- **Location**: Cell 12 (lines 383-399)
- **Pattern**: Generator LLM creates solutions, Evaluator LLM validates/selects best one
- **Implementation**: Three agents generate emails, `sales_picker` agent evaluates and selects the best
- **Code**:
```python
sales_picker = Agent(
    name="sales_picker",
    instructions="You pick the best cold sales email from the given options..."
)
best = await Runner.run(sales_picker, emails)
```
- **Key**: Quality assurance through evaluation and selection

### 3. **Orchestrator-Worker Pattern**
- **Location**: Cell 26 (lines 624-629)
- **Pattern**: Central LLM (orchestrator) coordinates specialized workers
- **Implementation**: Sales Manager orchestrates three worker agents (as tools) to generate emails
- **Key**: Agent decides which workers to call and when, more flexible than fixed parallelization

### 4. **Tool-Based Architecture**
- **Location**: Multiple cells (18, 22, 24)
- **Pattern**: Functions and agents can be converted to tools for agent use
- **Implementation**: 
  - `@function_tool` decorator converts functions to tools
  - `agent.as_tool()` converts agents to tools
- **Key**: Enables agents to call functions and delegate to other agents

### 5. **Handoff Pattern**
- **Location**: Cell 33 (lines 780-785), Cell 36 (lines 642-646)
- **Pattern**: Agent can delegate control to another agent, passing control across
- **Implementation**: Sales Manager hands off to Email Manager for formatting and sending
- **Key**: Control passes to another agent rather than returning to the caller

---

## The Critical Line: Workflow → Agent Transformation

### The ONE LINE that changes this from "Agentic Workflow" to "Agent"

**Location**: Cell 26, line 624

```python
sales_manager = Agent(name="Sales Manager", instructions=instructions, tools=tools, model="gpt-4o-mini")
                                                                     ^^^^^^^^^^^^
                                                                     THIS IS THE LINE
```

### Before (Workflow - Code Controls):
```python
# Cell 10-12: Code explicitly controls execution flow
results = await asyncio.gather(
    Runner.run(sales_agent1, message),
    Runner.run(sales_agent2, message),
    Runner.run(sales_agent3, message),
)
outputs = [result.final_output for result in results]
best = await Runner.run(sales_picker, emails)  # Code decides when to call picker
```
- **Control**: Code explicitly decides when and how to call each agent
- **Flow**: Predetermined, sequential/parallel execution
- **Decision-making**: Programmer controls the orchestration

### After (Agent - Agent Controls):
```python
# Cell 26: Agent autonomously decides which tools to use
sales_manager = Agent(
    name="Sales Manager", 
    instructions=instructions, 
    tools=tools,  # <-- THIS LINE: Gives agent autonomy
    model="gpt-4o-mini"
)
result = await Runner.run(sales_manager, message)  # Agent decides what to do
```
- **Control**: Agent autonomously decides which tools to call and when
- **Flow**: Agent-driven, dynamic execution based on reasoning
- **Decision-making**: Agent controls the orchestration through tool selection

### Why `tools=tools` is the Critical Line:

According to Anthropic's definition:
- **Workflow**: Code controls the execution flow - you programmatically decide when to call each component
- **Agent**: The agent itself decides what to do next - it has autonomy to choose from available tools

By adding `tools=tools` to the Agent constructor, you give the Sales Manager agent:
1. **Autonomy**: It can decide which tools to call
2. **Reasoning**: It evaluates the situation and chooses actions
3. **Control**: It orchestrates the workflow, not your code

The Sales Manager agent now has access to:
- `sales_agent1`, `sales_agent2`, `sales_agent3` (as tools)
- `send_email` (as a tool)

And it autonomously decides:
- Whether to call all three agents or just some
- In what order to call them
- When to send the email
- Whether to retry or adjust based on results

**Without `tools=tools`**: Your code controls everything (workflow)  
**With `tools=tools`**: The agent controls the execution (true agent)

---

## Summary

**Agentic Patterns Identified:**
1. Parallelization
2. Evaluator-Optimizer  
3. Orchestrator-Worker
4. Tool-Based Architecture
5. Handoff Pattern

**The Transformation:**
- **Before**: `asyncio.gather()` - Code controls flow (workflow)
- **After**: `tools=tools` - Agent controls flow (agent)

The single parameter `tools=tools` transforms the system from a code-controlled workflow to an agent-controlled autonomous system!

