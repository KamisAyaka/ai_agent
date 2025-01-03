from flask import Flask, request, jsonify, render_template
from langchain_core.messages import HumanMessage

from teacher.English_agent import app_english
from teacher.Chinese_agent import app_chinese
from teacher.combined_agent import app_combined
from teacher.Math_agent import app_math


def get_response(app, query):
    input_messages = [HumanMessage(query)]
    config = {"configurable": {"thread_id": "abc123"}}
    output = app.invoke({"messages": input_messages}, config)
    return output["messages"][-1].content


def choose_app(app_choice):
    if app_choice == '1':
        return app_math
    elif app_choice == '2':
        return app_chinese
    elif app_choice == '3':
        return app_english
    elif app_choice == '4':
        return app_combined
    else:
        print("无效的选择，默认使用综合老师")
        return app_combined


def main():
    app = choose_app('4')  # 初始选择综合老师

    while True:
        query = input("请输入您的问题（或输入 'exit' 退出,输入 'change' 更换老师）：")
        if query.lower() == 'exit':
            break
        elif query.lower() == 'change':
            app = choose_app(input("请输入选项（1/2/3/4）："))  # 切换老师
            continue
        response = get_response(app, query)
        print("回答:", response)


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response_route():
    data = request.form  # 修改为处理表单数据
    query = data.get('query')
    app_choice = data.get('app_choice')
    app = choose_app(app_choice)
    response = get_response(app, query)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
