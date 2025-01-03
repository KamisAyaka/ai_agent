from langchain_core.messages import HumanMessage

from English_agent import app_english
from Chinese_agent import app_chinese
from combined import app_combined
from Math_agent import app_math


def get_response(app, query):
    input_messages = [HumanMessage(query)]
    config = {"configurable": {"thread_id": "abc123"}}
    output = app.invoke({"messages": input_messages}, config)
    return output["messages"][-1].content


def choose_app():
    print("请选择一个老师：")
    print("1. 数学老师")
    print("2. 语文老师")
    print("3. 英语老师")
    print("4. 综合老师")
    choice = input("请输入选项（1/2/3/4）：")

    if choice == '1':
        return app_math
    elif choice == '2':
        return app_chinese
    elif choice == '3':
        return app_english
    elif choice == '4':
        return app_combined
    else:
        print("无效的选择，默认使用综合老师")
        return app_combined


def main():
    app = choose_app()  # 初始选择老师

    while True:
        query = input("请输入您的问题（或输入 'exit' 退出,输入 'change' 更换老师）：")
        if query.lower() == 'exit':
            break
        elif query.lower() == 'change':
            app = choose_app()  # 切换老师
            continue
        response = get_response(app, query)
        print("回答:", response)


if __name__ == "__main__":
    main()
