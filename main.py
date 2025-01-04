from langchain_core.messages import HumanMessage

from flask import Flask, request, jsonify, render_template

from obs import ObsClient
from config import OBS_ACCESS_KEY, OBS_SECRET_KEY, OBS_BUCKET_NAME, Endpoint
from langchain_community.document_loaders.obs_file import OBSFileLoader

from teacher.Chinese_agent import app_chinese
from teacher.English_agent import app_english
from teacher.Math_agent import app_math
from teacher.combined_agent import app_combined


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


app = Flask(__name__)

# 创建OBS客户端
obs_client = ObsClient(
    access_key_id=OBS_ACCESS_KEY,
    secret_access_key=OBS_SECRET_KEY,
    server=Endpoint)


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


@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    data = request.get_json()
    user_id = data.get('userId')
    conversation = data.get('conversation')

    if user_id and conversation:
        try:
            obs_client.putContent(bucketName=OBS_BUCKET_NAME, objectKey=f'{user_id}_conversation.txt',
                                  content=conversation)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid request data'}), 400


@app.route('/load_conversation', methods=['POST'])
def load_conversation():
    data = request.get_json()
    user_id = data.get('userId')

    if user_id:
        try:
            loader = OBSFileLoader(
                bucket=OBS_BUCKET_NAME,
                key=f'{user_id}_conversation.txt',
                endpoint=Endpoint,
                access_key_id=OBS_ACCESS_KEY,
                secret_access_key=OBS_SECRET_KEY,
            )
            response = loader.load()
            conversation = response['Body'].read().decode('utf-8')
            return jsonify({'conversation': conversation})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid request data'}), 400


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


if __name__ == "__main__":
    app.run(debug=True)
