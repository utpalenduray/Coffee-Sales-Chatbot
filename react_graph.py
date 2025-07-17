from langgraph.graph.message import add_messages, AnyMessage
from typing import TypedDict, Annotated
from langchain_core.messages import SystemMessage, RemoveMessage
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from systemPrompt import ASSISTANT_PROMPT
from langgraph_tools import execute_sql_query, plot_graph

class AgentGraph:
    def __init__(self, model):
        self.prompt_template = ASSISTANT_PROMPT
        self.memory = MemorySaver()
        # This is important: create the LLM bound to tools
        self.tools=[execute_sql_query, plot_graph]
        self.llm_with_tools = model.bind_tools(self.tools)

        # Build the graph
        self.react_graph = self._build_graph()

    def _build_graph(self):
        # Define AgentState inside the class so it's scoped here
        class AgentState(TypedDict):
            messages: Annotated[list, add_messages]

        # Define the nodes
        def filter_messages(state: AgentState):
            latest_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-4]]
            return {"messages": latest_messages}

        def assistant(state: AgentState):
            user_query = state['messages']
            system_message = self.prompt_template.format(user_query=user_query)
            system_message = SystemMessage(content=system_message)
            agent_response = self.llm_with_tools.invoke([system_message] + state["messages"])
            state["messages"].append(agent_response)
            return state

        # Construct the workflow
        workflow = StateGraph(AgentState)
        workflow.add_node("filter_messages", filter_messages)
        workflow.add_node("assistant", assistant)
        workflow.add_node("tools", ToolNode(self.tools))

        workflow.add_edge(START, "filter_messages")
        workflow.add_edge("filter_messages", "assistant")
        workflow.add_conditional_edges("assistant", tools_condition)
        workflow.add_edge("tools", "assistant")
        workflow.add_edge("assistant", END)

        return workflow.compile(checkpointer=self.memory)

    def get_graph(self):
        """
        Returns the compiled react_graph.
        """
        return self.react_graph