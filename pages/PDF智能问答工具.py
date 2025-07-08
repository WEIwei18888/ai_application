import streamlit as st
from utils.utils_pdf_qa_tool import qa_agent
from langchain.memory import ConversationBufferMemory

# 设置页面配置
st.set_page_config(
    page_title="PDF智能问答工具",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("✨ 智能PDF问答工具")

# 添加介绍性文字和分隔线
st.markdown("""
📖 欢迎使用智能PDF问答工具！\
本工具可以帮助你对PDF文档内容进行智能提问和快速获取答案，提升你的阅读与理解效率。
""")
st.markdown("---")

# 初始化上传组件的key
if "pdf_uploader_key" not in st.session_state:
    st.session_state["pdf_uploader_key"] = 0
    

# 侧边栏
with st.sidebar:
    openai_api_key = st.text_input("请输入你的OpenAI API密钥：", type="password")
    st.markdown("[获取Openai API密钥](https://platform.openai.com/api-keys)")

    # 重置按钮
    if st.button("🔄 重置聊天", type="secondary", help="点击此按钮将清除所有聊天记录和记忆。"):
        keys_to_clear = ["pdf_memory", "pdf_messages", "pdf_uploaded_file", "pdf_question"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state["pdf_uploader_key"] += 1  # 关键：让key变化
        st.experimental_rerun()  # 重新运行应用以清除状态


# 初始化记忆，储存进会话列表当中
if "pdf_memory" not in st.session_state:
    st.session_state["pdf_memory"]= ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        output_key="answer"
    )

# 将历史消息储存进会话状态中
if "pdf_messages" not in st.session_state:
    st.session_state["pdf_messages"] = []



# 将展示页面分为两列
column1, column2 = st.columns([4,1])

# 生成回答的逻辑
with column1:
    # 构架上传组件
    uploaded_file = st.file_uploader(
        "📂 上传你的PDF文件：",
        type="pdf",
        key=st.session_state["pdf_uploader_key"]  # 关键：用动态key
    )

    # 构建输入组件
    question = st.text_input(
        "❓ 对PDF的内容进行提问：",
        value=st.session_state.get("pdf_question", ""),
        disabled=not uploaded_file,
        placeholder="例如：这份文件主要讲了什么？",
        key="pdf_question"
    )
    submit = st.button("🚀 提交问题")

    if submit and not openai_api_key:
        st.info("请输入你的OpenAI API密钥。")
        st.stop()
    elif submit and not uploaded_file:
        st.info("请上传你的PDF文件。")
        st.stop()
    elif submit and not question:
        st.info("请输入你的问题。")
        st.stop()
    elif uploaded_file and question and openai_api_key and submit:
        with st.spinner("🧠 AI正在思考中，请稍后..."):
            response = qa_agent(openai_api_key, st.session_state["pdf_memory"], uploaded_file, question)
        st.divider()
        st.markdown("### ✅ 答案")

        # 检查result是否是字典并且包含"answer"键
        if isinstance(response, dict) and "answer" in response:
            st.write(response["answer"])

            # 更新聊天历史
            st.session_state["pdf_messages"].append({
                "role": "human",
                "content": question
            })
            st.session_state["pdf_messages"].append({
                "role": "ai",
                "content": response["answer"]
            })

            # 显示历史消息
            with st.expander("💬 历史消息："):
                for message in st.session_state["pdf_messages"]:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

            # 右侧列显示参考信息
            with column2:
                # 添加样式，使右侧列有左边框
                st.markdown(
                    """
                    <style>
                    div[data-testid="column"]:nth-of-type(2) {
                        border-left: 1px solid #CCCCCC;
                        padding-left: 15px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                # 将参考信息放入可折叠组件
                if "source_documents" in response and response["source_documents"]:
                    with st.expander("📚 参考片段"):
                        st.write("以下是AI回答所依据的文档片段：")
                        for i, document in enumerate(response["source_documents"]):
                            st.write(f"**片段 {i + 1}:**\n\n {document.page_content}")
                            if i < len(response["source_documents"]) - 1:
                                st.divider()
                else:
                    st.info("🔎 未找到相关参考片段。")

        else:
            st.error(response)  # 如果不是字典，就直接显示错误信息

