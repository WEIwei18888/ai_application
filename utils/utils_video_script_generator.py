from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.output_parsers import PydanticOutputParser
from pydantic.v1 import BaseModel, Field
from typing import List


# 定义大纲条目类
class OutlineItem(BaseModel):
    title: str = Field(description="章节标题")
    description: str = Field(description="章节简要描述")


# 定义分镜头条目类
class ShotItem(BaseModel):
    shot_number: int = Field(description="镜头编号")
    shot_type: str = Field(description="景别类型")
    visual_description: str = Field(description="画面描述")
    dialogue: str = Field(description="台词内容")
    duration: str = Field(description="镜头时长")


# 定义输出结果的类
class VideoScript(BaseModel):
    title: str = Field(description="视频脚本的标题")
    outline: List[OutlineItem] = Field(description="视频脚本的大纲列表")
    shot_list: List[ShotItem] = Field(description="视频脚本的分镜头列表")


# 定义生成脚本的函数工具
def generate_script(openai_api_key, subject, target_audience, video_type, video_length, creativity, style):
    try:
        # 定义出模型
        model = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key, base_url="https://api.aigc369.com/v1",
                           temperature=creativity)

        # 得到维基百科中主题相关的内容
        wikipedia = WikipediaAPIWrapper(lang="zh", top_k_results=3, doc_content_chars_max=1500)
        wikipedia_info = wikipedia.run(subject)

        # 定义出输出解析器
        output_parser = PydanticOutputParser(pydantic_object=VideoScript)

        # 定义出prompt
        system_template_text = """
        你是一位专业的视频脚本创作专家，擅长将复杂信息转化为观众易于理解的视觉叙事。你的任务是根据用户需求和提供的维基百科参考资料，创作一个结构清晰、创意新颖且具有可操作性的视频脚本。

        【创作要求】
        1. 脚本必须包含一个好的标题，标题要简洁明了，能够吸引观众
        2. 脚本必须包含两个主要部分：
            2.1 大纲 (outline)：包含多个章节，每个章节有标题和描述
            2.2 分镜头脚本 (shot_list)：包含多个镜头，每个镜头包含编号、景别、画面描述、台词和时长
        3. 根据目标受众调整专业术语的使用（如对普通大众需简化解释）
        4. 合理整合维基百科中的关键信息，但避免直接复制原文
        5. 突出主题的核心概念和用户可能感兴趣的知识点

        【大纲要求】
        - 每个大纲条目应包含清晰的章节标题和简要描述
        - 描述应融入维基百科关键信息
        - 大纲条目数量根据视频长度合理分配

        【分镜头脚本要求】
        - 每个镜头应包含：镜头编号、景别类型、画面描述、台词内容、时长
        - 画面描述应结合参考资料中的细节
        - 台词应解释核心概念，适合目标受众理解
        - 时长应根据视频总长度合理分配

        【参考资料处理指南】
        - 当维基百科资料包含多个主题时，聚焦与用户指定主题最相关的内容
        - 对专业术语进行简明易懂的解释，必要时使用类比或实例
        - 优先使用资料中的数据、案例和权威观点增强脚本可信度

        【重要提示】
        - 你必须严格按照指定的JSON格式输出结果
        - 确保title、outline和shot_list字段都有值
        - outline和shot_list必须是数组格式
        - 不要添加任何额外的文本或解释，只输出JSON格式的数据

        请严格遵循下面的输出格式：
        {parser_instructions}

        """

        human_template_text = """
        【主题】{subject}
        【目标受众】{target_audience}
        【视频类型】{video_type}
        【视频长度】{video_length}分钟
        【风格】{style}

        【维基百科参考资料】
        {wikipedia_info}

        请生成符合上述参数的视频脚本，确保内容准确且有深度，同时保持观众的兴趣：
        """

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_template_text),
            ("human", human_template_text)
        ])

        # 创建链
        chain = prompt_template | model | output_parser
        result = chain.invoke({
            "subject": subject,
            "target_audience": target_audience,
            "video_type": video_type,
            "video_length": video_length,
            "style": style,
            "wikipedia_info": wikipedia_info,
            "parser_instructions": output_parser.get_format_instructions()
        })

        return result, wikipedia_info
        
    except Exception as e:
        raise Exception(f"生成脚本时出现错误：{str(e)}")


