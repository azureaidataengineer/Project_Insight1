#SME agent

SME_llm = llm.bind_tools([get_schema, execute_sql])

SME_system_message = [SystemMessage(content="""You are a data SME Agent.
Use tools to answer the analyst's questions by querying the database.
you do not have to summarize it. Later Refiner will do that.""")]

class SMEState(TypedDict):
  messages: Annotated[list[AnyMessage], add_messages]

def SME(state: SMEState) -> SMEState:
  response = SME_llm.invoke(SME_system_message + state["messages"])
  return {"messages": [response]}


SME_graph = StateGraph(SMEState)
SME_graph.add_node("SME", SME)
SME_graph.add_node("tools", ToolNode([get_schema, execute_sql]))

SME_graph.add_edge(START, "SME")
SME_graph.add_conditional_edges("SME", tools_condition)
SME_graph.add_edge("tools","SME")

SME_app = SME_graph.compile()