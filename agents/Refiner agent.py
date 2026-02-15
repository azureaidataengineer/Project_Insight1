#Refiner agent

Refiner_llm = llm.bind_tools([generate_pdf_report])

Refiner_system_message = [SystemMessage(content="""You are an expert Refiner tasked with summarizing detailed database analysis reports.
Your goal is to produce a concise and clear summary in exactly eight lines.
Focus on key insights such as user count and growth, order statistics, top performers, and actionable recommendations.
Avoid repeating detailed tables or lists; instead, synthesize the information to highlight the main takeaways.
Keep the language simple and professional.
Make sure the summary is polished, easy to understand, and ready for presentation as a PDF document.
Give 2 actionable insights at the end to conclude
""")]

class RefinerState(TypedDict):
  messages: Annotated[list[AnyMessage], add_messages]

def Refiner(state: RefinerState) -> RefinerState:
  response = Refiner_llm.invoke(Refiner_system_message + state["messages"])
  return {"messages": [response]}


Refiner_graph = StateGraph(RefinerState)
Refiner_graph.add_node("Refiner", Refiner)
Refiner_graph.add_node("tools", ToolNode([generate_pdf_report]))

Refiner_graph.add_edge(START, "Refiner")
Refiner_graph.add_conditional_edges("Refiner", tools_condition)
Refiner_graph.add_edge("tools","Refiner")

Refiner_app = Refiner_graph.compile()