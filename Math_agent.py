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


# 定义预训练函数
def pretrain_math_teacher():
    # 预训练数据
    pretrain_data = [
        {"messages": [HumanMessage(content="你是数学老师。"), AIMessage(content="是的，我是一个数学老师。")]},
        {"messages": [HumanMessage(content="你叫什么名字？"), AIMessage(content="我的名字是数学老师。")]},
        {"messages": [HumanMessage(content="回答复杂的数学公式的时候可以使用latex格式进行回答")]},
        {"messages": [HumanMessage(content="What is 2 + 2?"), AIMessage(content="2 + 2 equals 4.")]},
        {"messages": [HumanMessage(content="What is the square root of 16?"),
                      AIMessage(content="The square root of 16 is 4.")]},
        # 添加更多预训练数据
    ]
    for data in pretrain_data:
        model.invoke(data["messages"])


# 调用预训练函数
pretrain_math_teacher()

# 定义数学老师的节点
workflow_math.add_edge(START, "math_teacher")
workflow_math.add_node("math_teacher", call_math_teacher)

# 添加记忆
memory = MemorySaver()
app_math = workflow_math.compile(checkpointer=memory)
