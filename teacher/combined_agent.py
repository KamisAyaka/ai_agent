from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

from config import model

# 定义综合老师的graph
workflow_combined = StateGraph(state_schema=MessagesState)


# 定义综合老师的函数
def call_combined_teacher(state: MessagesState):
    response = model.invoke(state["messages"])
    # 打印学习方案
    print("根据你的学习情况，以下是学习方案：")
    print(response)
    return {"messages": response}


# 定义预训练函数
def pretrain_combined_teacher():
    # 预训练数据
    pretrain_data = [
        {"messages": [HumanMessage(content="你是综合老师。"), AIMessage(content="是的，我是一个综合老师。")]},
        {"messages": [HumanMessage(content="请确保回答问题的时候全部使用中文回答"),
                      AIMessage(content="好的我会这样做的")]},
        {"messages": [HumanMessage(content="你的学习情况怎么样?"),
                      AIMessage(content="基于你的学习情况这是你的学习方案")]},
        # 添加更多预训练数据
    ]
    for data in pretrain_data:
        model.invoke(data["messages"])


# 调用预训练函数
pretrain_combined_teacher()

# 定义综合老师的节点
workflow_combined.add_edge(START, "combined_teacher")
workflow_combined.add_node("combined_teacher", call_combined_teacher)

# 添加记忆
memory = MemorySaver()
app_combined = workflow_combined.compile(checkpointer=memory)


