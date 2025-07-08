import streamlit as st
from utils.utils_clone_chatgpt import get_chat_response
from langchain.memory import ConversationBufferMemory

# 设置页面配置
st.set_page_config(
    page_title="智能对话助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 侧边栏
with st.sidebar:
    openai_api_key = st.text_input("请输入你的OpenAI API密钥：", type="password")
    st.markdown("[获取OpenAI API密钥](https://platform.openai.com/api-keys)")

    # "新对话"按钮逻辑保持不变
    if st.button("🔄 新对话", type="secondary", key="new_chat_button"):
        # 清除会话状态中的记忆和消息
        st.session_state["chat_memory"] = ConversationBufferMemory(return_messages=True)
        st.session_state["chat_messages"] = [{"role": "ai", "content": "你好，我是你的AI助手，有什么可以帮你的吗？"}]
        st.rerun()


# 页面标题
st.title("💬 智能对话助手")

#借助会话状态初始化记忆。只有在会话状态里面没有记忆的是时候，我们才会去初始化记忆
if "chat_memory" not in st.session_state:
    st.session_state["chat_memory"] = ConversationBufferMemory(return_messages=True)
    #为了便于之后我们在前端页面上展示对话，我们还可以在会话状态里去初始化一个messages类
    #这个消息列表的元素不能直接是内容，因为这样我们无法区分消息来自谁。我们可以让每个元素是一个字典
    #我们后续会借助一个叫做chat_message的函数，而它也是要区分消息所属角色的。它有两种使用方式
    st.session_state["chat_messages"] = [{"role": "ai", "content": "你好，我是你的AI助手，有什么可以帮你的吗？"}] #这两个会话状态变量，第一个是为了让模型有记忆，第二个是为了展示对话内容，想清楚这点

# 在页面上展示过往对话
for message in st.session_state["chat_messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# 聊天界面组件——聊天应用的输入框
prompt = st.chat_input("输入您的问题...")


# 生成聊天对话逻辑
if prompt: # 只有当用户输入了内容才执行以下逻辑
    if not openai_api_key:
        st.info(f"请输入您的API密钥")
    else:
        # 在发送请求给AI之前，我们先要把用户输入的内容储存进会话状态的messages列表里面，并且在网页上展示出来。不然用户会很奇怪，他刚才输入的内容哪里去了
        st.session_state["chat_messages"].append({"role": "human", "content": prompt})
        with st.chat_message("human"):
            st.write(prompt)
        # 得到AI的回复
        with st.spinner("🧠 AI正在思考中，请稍候..."):
            response = get_chat_response(openai_api_key, prompt, st.session_state["chat_memory"])
        st.session_state["chat_messages"].append({"role": "ai", "content": response})
        with st.chat_message("ai"):
            st.write(response)
