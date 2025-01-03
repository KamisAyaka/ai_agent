from config import model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

# 定义语文老师的graph
workflow_chinese = StateGraph(state_schema=MessagesState)


# 定义语文老师的函数
def call_chinese_teacher(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


# 定义语文老师的节点
workflow_chinese.add_edge(START, "chinese_teacher")
workflow_chinese.add_node("chinese_teacher", call_chinese_teacher)

# 添加记忆
memory = MemorySaver()
app_chinese = workflow_chinese.compile(checkpointer=memory)
