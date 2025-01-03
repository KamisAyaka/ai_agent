import os

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

from config import model


# 定义综合老师的graph
workflow_combined = StateGraph(state_schema=MessagesState)


# 定义综合老师的函数
def call_combined_teacher(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


# 定义综合老师的节点
workflow_combined.add_edge(START, "combined_teacher")
workflow_combined.add_node("combined_teacher", call_combined_teacher)

# 添加记忆
memory = MemorySaver()
app_combined = workflow_combined.compile(checkpointer=memory)
