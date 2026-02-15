# agents/sme_agent.py

from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from tools.execute_sql import execute_sql
from tools.get_schema import get_schema


# ==============================
# STATE
# ==============================

class SMEState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# ==============================
# SME AGENT
# ==============================

def get_sme_app():
    """
    Returns compiled SME agent graph
    """

    llm = ChatOpenAI(model="gpt-4o-mini")

    sme_llm = llm.bind_tools([get_schema, execute_sql])

    system_message = [
        SystemMessage(
            content="""
            You are a Data SME (Subject Matter Expert).
            Answer the analyst’s questions using database tools.
            Use get_schema first if needed.
            Then use execute_sql to fetch data.
            Do not summarize. Just provide detailed answers.
            """
        )
    ]

    def sme_node(state: SMEState) -> SMEState:
        response = sme_llm.invoke(system_message + state["messages"])
        return {"messages": [response]}

    graph = StateGraph(SMEState)

    graph.add_node("sme", sme_node)
    graph.add_node("tools", ToolNode([get_schema, execute_sql]))

    graph.add_edge(START, "sme")
    graph.add_conditional_edges("sme", tools_condition)
    graph.add_edge("tools", "sme")

    return graph.compile()

