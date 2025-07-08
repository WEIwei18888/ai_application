import streamlit as st
import pandas as pd
from utils.utils_csv_analyzer import dataframe_agent


# 对图表绘制逻辑进行封装
def create_char(input_data, chart_type):
    # 创建Pandas DataFrame
    df_data = pd.DataFrame(input_data["data"], columns=input_data["columns"])
    df_data.set_index(input_data["columns"][0], inplace=True) #设置DataFrame的索引，索引会被用来表示图表的横轴
    if chart_type == "bar":
        st.bar_chart(df_data)
    if chart_type == "line":
        st.line_chart(df_data)
    if chart_type == "scatter":
        st.scatter_chart(df_data)


pd.DataFrame()
# 设置页面配置
st.set_page_config(
    page_title="CSV数据分析智能工具",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("📊 CSV数据分析智能工具")

# 应用介绍
st.markdown("✨ 一站式CSV数据分析平台，支持智能问答、自动可视化与表格提取，助你高效洞察数据价值！")

# 初始化 file_uploader_key
if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0

# 侧边栏
with st.sidebar:
    openai_api_key = st.text_input("请输入你的OpenAI API密钥：", type="password")
    st.markdown("[获取Openai API密钥](https://platform.openai.com/api-keys)")
    # 添加清空内容按钮
    if st.button("🗑️ 清空所有内容", type="secondary", key="clear_btn_sidebar"):
        for key in ["csv_df", "csv_query", "csv_response_dic"]:
            if key in st.session_state:
                del st.session_state[key]
        # 关键：重置 file_uploader_key
        st.session_state["file_uploader_key"] += 1
        st.experimental_rerun()

# 上传文件区
st.markdown("---")
file_uploaded = st.file_uploader(
    "📤 上传你的数据文件（CSV格式）：",
    type="csv",
    key=st.session_state["file_uploader_key"]  # 关键：绑定 key
)

if file_uploaded:
    # 将上传文件转换为DataFrame，存储到会话状态中去
    st.session_state["csv_df"] = pd.read_csv(file_uploaded)
    with st.expander("📄 原始数据："):
        st.dataframe(st.session_state["csv_df"])
elif "csv_df" in st.session_state:
    # 如果文件被清除，也清除session_state中的csv_df
    del st.session_state["csv_df"]

# 问题输入区
input_disabled = not ("csv_df" in st.session_state and st.session_state["csv_df"] is not None)
query = st.text_area("📝 请输入你的问题或指令",
                     disabled=input_disabled,
                     key="csv_query",
                     value=st.session_state.get("csv_query", ""),
                     placeholder="请输入你关于以上表格的问题，或数据提取请求，或可视化要求（支持散点图、折线图、条形图）：")

# 生成回答按钮
submit = st.button("🚀 生成回答")

# 生成回答的逻辑
if submit and not openai_api_key:
    st.info("请输入您的OpenAI API密钥。")
    st.stop()
if submit and not file_uploaded:
    st.info("请先上传您的数据文件（CSV格式）。")
    st.stop()
if submit and not query:
    st.info("请输入您的问题或指令。")
    st.stop()
if submit:
    with st.spinner("🧠 AI正在思考中，请稍候..."):
        response_dic = dataframe_agent(openai_api_key, st.session_state["csv_df"], query)
        st.session_state["csv_response_dic"] = response_dic

# 展示AI的回答（如果有）
if "csv_response_dic" in st.session_state:
    st.markdown("---")
    if "answer" in st.session_state["csv_response_dic"]:
        st.markdown("### 💡 AI的回答")
        st.write(st.session_state["csv_response_dic"]["answer"])

    if "table" in st.session_state["csv_response_dic"]:
        st.markdown("### 📄 数据表格")
        # 提取列名和数据
        columns = st.session_state["csv_response_dic"]["table"]["columns"]
        rows_data = st.session_state["csv_response_dic"]["table"]["data"]

        # 创建Pandas DataFrame
        response_df = pd.DataFrame(rows_data, columns=columns)

        # 传入table
        st.table(response_df)

    if "bar" in st.session_state["csv_response_dic"]:
        st.markdown("### 📊 条形图")
        create_char(st.session_state["csv_response_dic"]["bar"], "bar")
    if "line" in st.session_state["csv_response_dic"]:
        st.markdown("### 📈 折线图")
        create_char(st.session_state["csv_response_dic"]["line"], "line")
    if "scatter" in st.session_state["csv_response_dic"]:
        st.markdown("### 📉 散点图")
        create_char(st.session_state["csv_response_dic"]["scatter"], "scatter")

