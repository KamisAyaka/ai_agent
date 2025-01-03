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


# 定义预训练函数
def pretrain_english_teacher():
    # 预训练数据
    pretrain_data = [
        {"messages": [HumanMessage(content="你是英语老师。"), AIMessage(content="是的，我是一个英语老师。")]},
        {"messages": [HumanMessage(content="请确保回答问题的时候全部使用英语回答"),
                      AIMessage(content="Okay, I'll do that")]},
        {"messages": [HumanMessage(content="How are you?"), AIMessage(content="I'm fine, thank you!")]},
        {"messages": [HumanMessage(content="What is your name?"), AIMessage(content="I am an AI assistant.")]},
        # 添加更多预训练数据
    ]
    for data in pretrain_data:
        model.invoke(data["messages"])


# 调用预训练函数
pretrain_english_teacher()

# 定义英语老师的节点
workflow_english.add_edge(START, "english_teacher")
workflow_english.add_node("english_teacher", call_english_teacher)

# 添加记忆
memory = MemorySaver()
app_english = workflow_english.compile(checkpointer=memory)
