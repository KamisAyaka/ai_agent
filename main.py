import json

from langchain_core.messages import HumanMessage

from flask import Flask, request, jsonify, render_template, redirect, url_for, session

from obs import ObsClient
from config import OBS_ACCESS_KEY, OBS_SECRET_KEY, OBS_BUCKET_NAME, Endpoint
from langchain_community.document_loaders.obs_file import OBSFileLoader

from teacher.Chinese_agent import app_chinese
from teacher.English_agent import app_english
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


app = Flask(__name__)

# 设置 Flask 应用的 secret_key
app.secret_key = '123456'  # 替换为一个唯一的密钥

# 创建OBS客户端
obs_client = ObsClient(
    access_key_id=OBS_ACCESS_KEY,
    secret_access_key=OBS_SECRET_KEY,
    server=Endpoint)

config = {
    "ak": OBS_ACCESS_KEY,
    "sk": OBS_SECRET_KEY
}


def save_user(user_id, user_data):
    """
    将用户数据保存到OBS中
    :param user_id: 用户ID
    :param user_data: 用户数据（字典）
    """
    object_key = f'users/{user_id}.json'
    user_data_json = json.dumps(user_data)
    resp = obs_client.putContent(bucketName=OBS_BUCKET_NAME, objectKey=object_key, content=user_data_json)
    if resp.status < 300:
        print(f"User {user_id} saved successfully.")
    else:
        print(f"Failed to save user {user_id}. Error: {resp.error_code} {resp.error_msg}")


def load_user(user_id):
    """
    从OBS中加载用户数据
    :param user_id: 用户ID
    :return: 用户数据（字典），如果用户不存在则返回None
    """
    object_key = f'users/{user_id}.json'
    try:
        resp = obs_client.getObject(bucketName=OBS_BUCKET_NAME, objectKey=object_key, loadStreamInMemory=True)
        if resp.status < 300:
            user_data_json = resp.body['buffer'].decode('utf-8')
            user_data = json.loads(user_data_json)
            print(f"Loaded user data for {user_id} from path: {object_key}, data: {user_data}")  # 调试信息
            return user_data
        else:
            print(f"Failed to load user {user_id} from path: {object_key}. Error: {resp.error_code} {resp.error_msg}")
            return None
    except Exception as e:
        print(f"Exception occurred while loading user {user_id}: {e}")
        return None


# 首页：登录界面
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')  # 登录页面


# 注册界面
@app.route('/register')
def register_page():
    return render_template('register.html')  # 注册页面


# 登录处理
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = load_user(username)

    if user is None:
        return jsonify({"error": "用户名不存在，请注册后登录！"}), 400
    elif user['password'] != password:
        return jsonify({"error": "密码错误，请重试！"}), 400
    else:
        session['username'] = username
        return jsonify({"message": f"欢迎回来，{username}！"})


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    # 检查用户是否已存在
    user = load_user(username)

    if user is not None:
        print(f"User {username} already exists.")  # 调试信息
        return jsonify({"error": "用户名已存在，请选择其他用户名！"}), 400
    else:
        # 保存新用户数据，确保保存的是一个字典
        user_data = {"password": password}
        save_user(username, user_data)
        print(f"User {username} registered successfully with data: {user_data}")  # 调试信息
        return jsonify({"message": f"注册成功，欢迎您，{username}！"})


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


# 仪表盘
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', username=session['username'])


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
                key=f'users/{user_id}.json',
                endpoint=Endpoint,
                config=config
            )
            response = loader.load()
            conversation = response['Body'].read().decode('utf-8')
            return jsonify({'conversation': conversation})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid request data'}), 400


if __name__ == "__main__":
    app.run(debug=True)
