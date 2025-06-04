from typing import TypedDict, Annotated, List, Union, Optional, Literal , Tuple
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
import operator
# from typing import List, Tuple, Optional, Literal, Union, TypedDict, Annotated

from backend.services.client import get_llm
from backend.services.tools import get_tools

# --- Agent State --- #
class AgentState(TypedDict):
    input: str # User's initial input
    chat_history: List[BaseMessage] # Full conversation history
    agent_outcome: Optional[Union[AgentAction, AgentFinish, List[AgentAction]]] # Intermediate step for tool use
    intermediate_steps: Annotated[List[tuple[AgentAction, str]], operator.add] # Tool execution results
    
    # Fields for goal detection and clarification
    user_goal: Optional[Literal['lose_weight', 'gain_weight', 'stay_healthy', 'unknown']] # Detected user goal
    clarification_needed: bool # Flag if clarification is required
    clarification_questions_asked: int # Counter for clarification attempts
    
    # Fields for contextual information (optional, for log awareness)
    user_logs_summary: Optional[str] # Summary of user's recent logs

# --- Pydantic Models for LLM Structured Output --- #
class GoalIdentification(BaseModel):
    """Represents the identified user goal and need for clarification."""
    goal: Literal['lose_weight', 'gain_weight', 'stay_healthy', 'unknown'] = Field(description="The user's primary health goal. Set to 'unknown' if unclear.")
    requires_clarification: bool = Field(description="True if the user's input is ambiguous or incomplete and requires follow-up questions.")
    reasoning: Optional[str] = Field(description="Brief explanation for why clarification is or isn't needed.")

class PlanDecision(BaseModel):
    """Decision on whether to use tools or respond directly."""
    should_use_tools: bool = Field(description="True if tools are needed to answer the user's query, False otherwise.")
    reasoning: Optional[str] = Field(description="Brief explanation for the decision.")

# --- LangGraph Nodes --- # 

llm = get_llm()
all_tools = get_tools()
# tool_executor = ToolExecutor(all_tools) # ToolExecutor might be deprecated or moved

# 1. Goal Analysis Node
def analyze_goal_node(state: AgentState):
    """Analyzes the user's input to identify their goal and if clarification is needed."""
    print("--- ANALYZING GOAL ---")
    structured_llm_goal = llm.with_structured_output(GoalIdentification)
    
    prompt = f"""
    You are an AI assistant helping a user with their health and nutrition goals. 
    Analyze the following user input and conversation history to determine their main goal and if clarification is needed.
    User goals can be: 'lose_weight', 'gain_weight', 'stay_healthy'. If the goal is not clear, set it to 'unknown'.
    
    Consider if the input is ambiguous or incomplete. For example, if the user says 'I want to be healthier' without specifics, clarification is needed.
    If clarification is needed, you will later ask questions like:
    - "What is your specific health goal (e.g., lose weight, gain muscle, improve energy)?"
    - "Do you have a timeframe in mind to achieve this goal?"
    - "Do you exercise regularly? If so, what kind and how often?"
    - "Are there any health conditions, allergies, or dietary restrictions I should be aware of?"

    Conversation History:
    {state['chat_history']}
    
    User Input: {state['input']}
    
    Based on the input and history, identify the goal and whether clarification is required.
    """
    
    goal_analysis: GoalIdentification = structured_llm_goal.invoke(prompt)
    
    print(f"Goal Analysis Result: {goal_analysis}")
    
    return {
        "user_goal": goal_analysis.goal,
        "clarification_needed": goal_analysis.requires_clarification,
        "clarification_questions_asked": state.get("clarification_questions_asked", 0) # Initialize if not present
    }

# 2. Clarification Node (if needed)
def clarification_node(state: AgentState):
    """Asks clarifying questions if the user's goal is unclear."""
    print("--- ASKING CLARIFICATION QUESTIONS ---")
    questions = [
        "What is your specific health goal (e.g., lose weight, gain muscle, improve energy)?",
        "Do you have a timeframe in mind to achieve this goal?",
        "Do you exercise regularly? If so, what kind and how often?",
        "Are there any health conditions, allergies, or dietary restrictions I should be aware of?"
    ]
    
    # Simple strategy: ask one question at a time, or a combined message
    # For this example, let's combine them for the first clarification attempt.
    clarification_prompt = "To help you better, I need a little more information. Could you please tell me: \n" + "\n".join(f"- {q}" for q in questions)
    
    return {
        "agent_outcome": AgentFinish(return_values={"output": clarification_prompt}, log=clarification_prompt),
        "clarification_questions_asked": state.get("clarification_questions_asked", 0) + 1
    }

# 3. Planning Node (Decide to use tools or respond directly)
def planning_node(state: AgentState):
    """Decides whether to use tools or generate a direct response based on the clear goal."""
    print("--- PLANNING: DECIDING ON TOOL USE ---")
    structured_llm_plan = llm.with_structured_output(PlanDecision)
    
    # Optional: Incorporate user log summary if available
    log_context = ""
    if state.get("user_logs_summary"):
        log_context = f"\nUser's Recent Log Summary:\n{state['user_logs_summary']}"

    prompt = f"""
    You are an AI health assistant. The user's goal is now considered clear: '{state['user_goal']}'.
    Conversation History:
    {state['chat_history']}
    User Input: {state['input']}
    {log_context}

    Available tools: {[tool.name for tool in all_tools]}
    Tool descriptions:
    {[f'{tool.name}: {tool.description}' for tool in all_tools]}

    Based on the user's input, their stated goal ('{state['user_goal']}'), and conversation history, decide if you need to use any tools to formulate a comprehensive plan or answer. 
    For example:
    - If goal is 'lose_weight', you might need BMI, BMR, and calorie_estimator.
    - If goal is 'gain_weight', similar tools might be needed.
    - If goal is 'stay_healthy' and input is general, a direct response might suffice unless specific metrics are asked for.
    - If the user asks for external information (e.g., 'What are the benefits of Omega-3?'), consider the search tool if available.
    
    Respond with whether tools are needed.
    """
    
    plan_decision: PlanDecision = structured_llm_plan.invoke(prompt)
    print(f"Planning Decision: {plan_decision}")

    if plan_decision.should_use_tools:
        # If tools are needed, the agent_node will be called next to select them
        # We don't return agent_outcome here, agent_node will create it.
        print("Decision: Use tools.")
        return {}
    else:
        # No tools needed, proceed to generate a direct response
        print("Decision: Respond directly.")
        # This will be handled by the 'generate_response_node' if no tools are chosen by agent_node
        # or if planning_node decides no tools are needed.
        # To directly go to response node, we can simulate an AgentFinish without tool usage.
        # However, the standard flow is to let agent_node make the final call or generate response.
        # For simplicity here, if planning says no tools, we'll let agent_node confirm that.
        return {}

# 4. Agent Node (LangChain's ReAct-like logic for tool invocation or direct response)
def agent_node(state: AgentState):
    """Invokes the LLM to use tools or generate a response. This is the main ReAct-style agent logic."""
    print("--- AGENT: EXECUTING/RESPONDING ---")
    
    # Optional: Incorporate user log summary if available
    log_context = ""
    if state.get("user_logs_summary"):
        log_context = f"\nUser's Recent Log Summary:\n{state['user_logs_summary']}"

    # Construct messages for the LLM, including history and current input
    # The system prompt guides the LLM on how to behave based on the current state (goal, tools needed etc.)
    system_prompt = f"""You are an AI Health and Nutrition Assistant.
    Your current task is to respond to the user based on their input and identified goal: '{state['user_goal']}'.
    Conversation History is provided.
    {log_context}
    
    You have access to the following tools:
    {[f'{tool.name}: {tool.description}' for tool in all_tools]}
    
    Follow these instructions:
    1. If the user's query can be answered directly or a plan can be provided without specific calculations yet, respond directly.
    2. If you need to calculate BMI, BMR, estimate calories, or summarize logs, invoke the necessary tools.
    3. If the user asks for external information (e.g., 'What are benefits of Omega-3?'), use the 'tavily_search_results_json' tool if available and appropriate.
    4. Formulate a thoughtful, empathetic, and actionable response.
    5. If providing a plan (e.g., for weight loss), explain the components (e.g., calorie target, meal suggestions, exercise types).
    
    Based on the user's goal of '{state['user_goal']}', their input '{state['input']}', and the conversation history, decide whether to call a tool or respond directly. 
    If you are calling a tool, ensure you have all necessary parameters from the conversation or ask if missing. 
    If responding directly, provide a comprehensive answer or plan.
    """
    
    messages = [HumanMessage(content=system_prompt)] # System prompt as HumanMessage for some models
    messages.extend(state['chat_history'])
    messages.append(HumanMessage(content=state['input']))

    # The LLM decides whether to call a tool or respond directly.
    # We bind the tools to the LLM so it knows how to format tool calls.
    agent_llm_with_tools = llm.bind_tools(all_tools)
    
    # Invoke the LLM
    # If the LLM decides to call a tool, it will return a message with `tool_calls` attribute
    # If it decides to respond directly, it will return a standard AIMessage content
    ai_response_message = agent_llm_with_tools.invoke(messages)
    
    if not ai_response_message.tool_calls:
        print(f"Agent: Responding directly. AI Response: {ai_response_message.content}")
        return {"agent_outcome": AgentFinish(return_values={"output": ai_response_message.content}, log=ai_response_message.content)}
    else:
        print(f"Agent: Calling tools. AI Tool Calls: {ai_response_message.tool_calls}")
        # Convert AIMessage with tool_calls to AgentAction(s)
        actions = []
        for tool_call in ai_response_message.tool_calls:
            actions.append(ToolInvocation(tool=tool_call["name"], tool_input=tool_call["args"]))
        
        # LangGraph expects AgentAction for tool execution, not ToolInvocation directly in this part of the typical agent loop.
        # However, ToolExecutor can take ToolInvocation. For simplicity in this custom loop, 
        # we'll prepare it for a structure that ToolExecutor can handle or adapt if needed.
        # The key is that `tool_executor.invoke(action)` expects an AgentAction or ToolInvocation.
        # Let's assume for now the structure from `ai_response_message.tool_calls` is sufficient
        # or can be mapped to what ToolExecutor expects if we pass it directly.
        # For a more robust ReAct loop, one would typically convert tool_calls to AgentAction instances.
        
        # For now, let's prepare it as if it's going to the ToolExecutor which can handle ToolInvocation
        # The `agent_outcome` will be processed by the `tool_execution_node`
        return {"agent_outcome": actions} # actions is a list of ToolInvocation

# 5. Tool Execution Node
def tool_execution_node(state: AgentState):
    """Executes the tools chosen by the agent and returns the results."""
    print("--- EXECUTING TOOLS --- ")
    agent_actions = state["agent_outcome"] # This should be List[ToolInvocation]
    
    if not isinstance(agent_actions, list):
        # Handle cases where it might be a single action, though LLM tool_calls usually gives a list
        agent_actions = [agent_actions]

    outputs = []
    for action in agent_actions:
        # action here is expected to be a ToolInvocation or similar structure that tool_executor can handle
        # If it was an AgentAction, it would be action.tool, action.tool_input
        print(f"Executing tool: {action.tool} with input {action.tool_input}")
        # The tool_executor.invoke expects a single ToolInvocation or AgentAction
        # If agent_outcome is a list of ToolInvocations, we iterate and execute.
        tool_to_execute = next((t for t in all_tools if t.name == action.tool), None)
        if tool_to_execute:
            try:
                observation = tool_to_execute.invoke(action.tool_input)
            except Exception as e:
                observation = f"Error executing tool {action.tool}: {e}"
                print(f"Error: {observation}")
        else:
            observation = f"Tool {action.tool} not found."
            print(f"Error: {observation}")
        
        outputs.append(
            (ToolMessage(content=str(observation), tool_call_id=action.tool_call_id if hasattr(action, 'tool_call_id') else None) if isinstance(action, ToolInvocation) else (action, str(observation)))
        )
        # The structure for intermediate_steps is typically List[Tuple[AgentAction, str]]
        # We need to adapt if action is ToolInvocation. For now, storing as (ToolInvocation, observation string)
        # Or convert ToolInvocation to a mock AgentAction for storage if strict ReAct format is needed for `intermediate_steps`
        # For simplicity, let's assume this structure is okay for now or adapt later if LangGraph complains.
        # A more robust way: if action is ToolInvocation, create a dummy AgentAction for the tuple.
        # mock_agent_action = AgentAction(tool=action.tool, tool_input=action.tool_input, log="")
        # outputs.append((mock_agent_action, str(observation)))

    print(f"Tool Results: {outputs}")
    return {"intermediate_steps": outputs}

# --- Conditional Edges --- #

def should_clarify(state: AgentState) -> Literal["clarification_node", "planning_node", "END"]:
    """Determines the next step after goal analysis."""
    print("--- DECISION: SHOULD CLARIFY? ---")
    if state.get("clarification_needed", False):
        if state.get("clarification_questions_asked", 0) < 2: # Limit clarification attempts
            print("Decision: Yes, clarify.")
            return "clarification_node"
        else:
            print("Decision: Max clarifications reached, ending.")
            # Update state to reflect that we're ending due to max clarifications
            # This might involve setting a specific agent_outcome to signal this to the user.
            # For now, just END. A more graceful exit would be to inform the user.
            # state['agent_outcome'] = AgentFinish(return_values={"output": "I've tried to clarify a few times, but I'm still unsure about your goal. Could you please try rephrasing your request?"}, log="Max clarifications reached.")
            return END # Or a specific 'max_clarification_response_node'
    print("Decision: No, goal is clear. Proceed to planning.")
    return "planning_node"

def after_planning_or_agent(state: AgentState) -> Literal["tool_execution_node", "agent_node", "END"]:
    """Routes after the planning node or after the agent node if no tools were called initially by planning."""
    print("--- DECISION: AFTER PLANNING / AGENT ---")
    if isinstance(state.get("agent_outcome"), AgentFinish):
        print("Agent decided to finish (responded directly). Ending interaction.")
        return END
    elif isinstance(state.get("agent_outcome"), list) and all(isinstance(item, ToolInvocation) for item in state.get("agent_outcome")):
        print("Agent decided to use tools. Proceed to tool execution.")
        return "tool_execution_node"
    # This case implies planning_node decided no tools, or agent_node needs to run first if planning was skipped or deferred decision
    # If agent_outcome is not set or not AgentFinish/ToolInvocation list, it means agent_node should run (or re-run if it was a pass-through from planning)
    print("Proceeding to agent node (either first run after planning or re-run after tools).")
    return "agent_node" 
    # If planning_node decided NO tools, agent_node should be called to generate a direct response.
    # If agent_node was already called and returned AgentFinish, the first condition handles it.
    # If agent_node was called and returned ToolInvocations, the second condition handles it.
    # This path is for when planning_node says 'no tools' -> agent_node (to generate response)
    # Or after tool_execution_node -> agent_node (to process tool results and respond)

# --- Build the Graph --- #
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("analyze_goal_node", analyze_goal_node)
workflow.add_node("clarification_node", clarification_node) # This node directly leads to END for now after asking.
workflow.add_node("planning_node", planning_node)
workflow.add_node("agent_node", agent_node) # Main agent logic (tool use or direct response)
workflow.add_node("tool_execution_node", tool_execution_node)

# Set entry point
workflow.set_entry_point("analyze_goal_node")

# Add conditional edges
workflow.add_conditional_edges(
    "analyze_goal_node",
    should_clarify,
    {
        "clarification_node": "clarification_node", # If clarification needed
        "planning_node": "planning_node",       # If goal is clear
        END: END                            # If max clarifications reached (not fully implemented yet)
    }
)

# After clarification, the user would respond, and the flow would restart or go to a response processing node.
# For this simplified graph, clarification_node leads to END. A real app would loop back.
# A more complete flow: clarification_node -> (wait for user input) -> analyze_goal_node
# For now, let's assume clarification leads to an agent response and then ENDs this turn.
workflow.add_edge("clarification_node", END) # Simplified: clarification is a final response for the turn

# Conditional routing after planning_node or agent_node (if it decided to respond directly initially)
workflow.add_conditional_edges(
    "planning_node",
    after_planning_or_agent, # This logic decides if tools are needed (go to agent_node to pick them) or respond directly (agent_node will do that)
    {
        "agent_node": "agent_node", # If planning says use tools OR no tools (agent_node handles both by deciding tool call or direct response)
        "tool_execution_node": "tool_execution_node", # Should not happen directly from planning if agent_node is the one choosing tools
        END: END # Should not happen directly from planning if agent_node is the one responding
    }
)

# After agent node decides, it can either finish or lead to tool execution
workflow.add_conditional_edges(
    "agent_node",
    after_planning_or_agent, # Re-using this logic: if AgentFinish -> END, if ToolInvocations -> tool_execution_node
    {
        "tool_execution_node": "tool_execution_node",
        END: END
    }
)

# After tools are executed, results go back to the agent node to process and generate a final response
workflow.add_edge("tool_execution_node", "agent_node")

# Compile the graph
app = workflow.compile()

def run_assistant(user_input: str, chat_history: List[Tuple[str, str]] = [], current_goal: Optional[dict] = None):
    # Convert chat history to Langchain format
    converted_chat_history = []
    for human_msg, ai_msg in chat_history:
        converted_chat_history.append(HumanMessage(content=human_msg))
        converted_chat_history.append(AIMessage(content=ai_msg))

    # Initial state for the graph
    initial_state = {
        "input": user_input,
        "chat_history": converted_chat_history,
        "intermediate_steps": [],
        "user_goal": current_goal.get("goal_text") if current_goal else "unknown", # Pass goal from DB
        "clarification_needed": False, # Assume clarified if goal is passed
        "clarification_questions_asked": 0
    }

    # Run the graph
    final_state: AgentState = app.invoke(initial_state)

    # Extract the final response
    if isinstance(final_state["agent_outcome"], AgentFinish):
        return final_state["agent_outcome"].return_values["output"]
    else:
        # This case should ideally not be reached if the graph always ends with AgentFinish
        return "An unexpected error occurred or the assistant did not finalize its response."

def run_qa_assistant(user_input: str, chat_history: List[Tuple[str, str]] = []):
    # Convert chat history to Langchain format
    converted_chat_history = []
    for human_msg, ai_msg in chat_history:
        converted_chat_history.append(HumanMessage(content=human_msg))
        converted_chat_history.append(AIMessage(content=ai_msg))

    # Define a simple Q&A workflow without goal analysis or complex planning
    qa_workflow = StateGraph(AgentState)

    # Define a simple agent node for Q&A
    def qa_agent_node(state: AgentState):
        print("--- QA AGENT: RESPONDING DIRECTLY ---")
        messages = [
            HumanMessage(content="You are a helpful AI assistant. Respond to the user's query.")
        ]
        messages.extend(state['chat_history'])
        messages.append(HumanMessage(content=state['input']))

        ai_response_message = llm.invoke(messages)
        return {"agent_outcome": AgentFinish(return_values={"output": ai_response_message.content}, log=ai_response_message.content)}

    qa_workflow.add_node("qa_agent", qa_agent_node)
    qa_workflow.set_entry_point("qa_agent")
    qa_workflow.add_edge("qa_agent", END)

    qa_app = qa_workflow.compile()

    initial_state = {
        "input": user_input,
        "chat_history": converted_chat_history,
        "intermediate_steps": []
    }

    final_state: AgentState = qa_app.invoke(initial_state)

    if isinstance(final_state["agent_outcome"], AgentFinish):
        return final_state["agent_outcome"].return_values["output"]
    else:
        return "An unexpected error occurred in Q&A assistant."


# Example usage (for testing)
if __name__ == '__main__':
    # Test 1: Clear goal, should use tools
    print("\n--- Test 1: Lose Weight (Clear Goal, Expect Tools) ---")
    # response1 = run_assistant("I want to lose 10 pounds. I am 30 years old, male, 75kg, 170cm, and I do light exercise.")
    # print(f"Assistant: {response1}")

    # Test 2: Ambiguous goal, should ask for clarification
    print("\n--- Test 2: Be Healthier (Ambiguous, Expect Clarification) ---")
    # response2 = run_assistant("I want to be healthier.")
    # print(f"Assistant: {response2}")
    
    # Test 3: Follow-up after clarification (simulated)
    print("\n--- Test 3: Follow-up after Clarification ---")
    # history3 = [("I want to be healthier.", "To help you better, I need a little more information. Could you please tell me: \n- What is your specific health goal (e.g., lose weight, gain muscle, improve energy)?\n- Do you have a timeframe in mind to achieve this goal?\n- Do you exercise regularly? If so, what kind and how often?\n- Are there any health conditions, allergies, or dietary restrictions I should be aware of?")]
    # response3 = run_assistant("My goal is to lose weight, about 5kg. I exercise 3 times a week. No major health issues.", chat_history=history3)
    # print(f"Assistant: {response3}")

    # Test 4: General question, might not need tools
    print("\n--- Test 4: General Advice (Stay Healthy) ---")
    # response4 = run_assistant("What are some tips to stay healthy?")
    # print(f"Assistant: {response4}")
    
    # Test 5: Question requiring Tavily Search (if configured)
    # print("\n--- Test 5: External Question (Tavily) ---")
    # Ensure TAVILY_API_KEY is set in your .env for this to work
    # response5 = run_assistant("What are the benefits of intermittent fasting?")
    # print(f"Assistant: {response5}")
    pass # Keep alive for prints