from config import model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults

# 定义语文老师的graph
workflow_chinese = StateGraph(state_schema=MessagesState)


# 定义语文老师的函数
def call_chinese_teacher(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": response}


# 定义预训练函数
def pretrain_chinese_teacher():
    # 预训练数据
    pretrain_data = [
        {"messages": [HumanMessage(content="你是语文老师。"), AIMessage(content="是的，我是一个语文老师。")]},
        {"messages": [HumanMessage(content="你好吗？"), AIMessage(content="我很好，谢谢！")]},
        {"messages": [HumanMessage(content="你的名字是什么？"), AIMessage(content="我是一个语文学习AI助手。")]},
        # 添加更多预训练数据
    ]
    for data in pretrain_data:
        model.invoke(data["messages"])


# 调用预训练函数
pretrain_chinese_teacher()

# 添加TavilySearchResults工具
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = model
llm_with_tools = llm.bind_tools(tools)

# 定义语文老师的节点
workflow_chinese.add_edge(START, "chinese_teacher")
workflow_chinese.add_node("chinese_teacher", call_chinese_teacher)

# 添加工具节点
tool_node = ToolNode(tools=[tool])
workflow_chinese.add_node("tools", tool_node)

# 添加条件边
workflow_chinese.add_conditional_edges(
    "chinese_teacher",
    tools_condition,
)
workflow_chinese.add_edge("tools", "chinese_teacher")

# 添加记忆
memory = MemorySaver()
app_chinese = workflow_chinese.compile(checkpointer=memory)
