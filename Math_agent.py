from config import model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

# 定义数学老师的graph
workflow_math = StateGraph(state_schema=MessagesState)


# 定义数学老师的函数
def call_math_teacher(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


# 定义数学老师的节点
workflow_math.add_edge(START, "math_teacher")
workflow_math.add_node("math_teacher", call_math_teacher)

# 添加记忆
memory = MemorySaver()
app_math = workflow_math.compile(checkpointer=memory)
