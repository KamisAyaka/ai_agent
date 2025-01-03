from config import model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph



# 定义英语老师的graph
workflow_english = StateGraph(state_schema=MessagesState)

# 定义英语老师的函数
def call_english_teacher(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}

# 定义英语老师的节点
workflow_english.add_edge(START, "english_teacher")
workflow_english.add_node("english_teacher", call_english_teacher)

# 添加记忆
memory = MemorySaver()
app_english = workflow_english.compile(checkpointer=memory)