from utils.utils_video_script_generator import generate_script
import streamlit as st

# 配置页面
st.set_page_config(
    page_title="视频脚本生成器",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

#应用标题
st.title("🎬 AI视频脚本生成器")

# 应用介绍
st.markdown("""
📜 AI智能生成视频脚本，自动输出镜头、台词与时长，助你高效完成视频创作。
""")

st.divider()

#侧边栏
with st.sidebar:
    openai_api_key = st.text_input("请输入你的OpenAI API密钥：", type="password", key="api_key")
    st.markdown("[获取Openai API密钥](https://platform.openai.com/api-keys)")
    
    # 添加清空按钮
    if st.button("🗑️ 清空所有内容", type="secondary"): #type="secondary" 将按钮的样式设置为次要（secondary）类型，通常颜色会比较柔和，与主要（primary）按钮区分开来。
        st.rerun() #重新运行整个 Streamlit 应用程序的脚本

#基础参数设置
st.markdown("### 📋 核心信息")
subject = st.text_input("🎯 请输入视频的主题：", placeholder="例如：智能手表的健康功能", key="subject")
video_type = st.text_input("🎥 请输入视频类型：", placeholder="例如：广告片、知识科普、产品教程、vlog", key="video_type")
target_audience = st.text_input("👥 请输入视频的目标受众：", placeholder="例如：儿童、职场人士、老年人", key="target_audience")
video_length = st.number_input("⏱️ 请输入视频时长（单位：分钟）：", min_value=0.1, step=0.1, value=1.0, key="video_length")

#创意风格
st.markdown("### 🎨 创意方向")
creativity = st.slider("💡 请输入你想要的创造力值（值越高越富有创意和突破性）：", min_value=0.0, max_value=1.0, step=0.1, value=0.7, key="creativity")
style = st.text_input("🎭 请输入你想要的视频风格：", placeholder="例如：幽默、科技感、治愈", key="style")


#提交按钮
st.markdown("")
submit = st.button("🚀 生成脚本")

if submit and not openai_api_key:
    st.info("请输入你的OpenAI API密钥")
    st.stop()
if submit and not subject:
    st.info("请输入你的视频主题")
    st.stop()
if submit and not video_type:
    st.info("请输入你的视频类型")
    st.stop()
if submit and not target_audience:
    st.info("请输入你的目标受众")
    st.stop()
if submit and not style:
    st.info("请输入你的视频风格")
    st.stop()

if submit:
    try:
        with st.spinner("🤔 AI正在思考中，请稍等..."):
            result, wikipedia_info = generate_script(openai_api_key, subject, target_audience, video_type, video_length, creativity, style)

        st.divider()

        st.markdown("### 生成结果")

        st.markdown("#### 📺 视频标题")
        st.write(result.title)
        
        st.markdown("#### 📝 脚本大纲")
        for i, outline_item in enumerate(result.outline, 1):
            st.markdown(f"**{i}. {outline_item.title}**")
            st.write(f"   {outline_item.description}")
        
        st.markdown("#### 🎬 分镜头脚本")
        # 创建表头
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown("**镜头编号**")
        with col2:
            st.markdown("**景别**")
        with col3:
            st.markdown("**画面描述**")
        with col4:
            st.markdown("**台词**")
        with col5:
            st.markdown("**时长**")
        st.markdown("---")
        # 显示每个镜头
        for shot in result.shot_list:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"**{shot.shot_number}**")
            with col2:
                st.markdown(f"*{shot.shot_type}*")
            with col3:
                st.write(shot.visual_description)
            with col4:
                st.write(shot.dialogue)
            with col5:
                st.markdown(f"*{shot.duration}*")
            st.markdown("---")

        with st.expander("📚 维基百科搜索结果"):
            st.info(wikipedia_info)
    except Exception as e:
        st.error(f"❌ 生成脚本时出现错误：{str(e)}")