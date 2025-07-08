from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import openai
import json

# table键对应的值是一个字典，这个字典里面，columns会对应表格的列名，data对应表格里面的内容
# bar键对应的值是一个字典，columns对应着图表的轴，data对应着里面的内容

PROMPT_TEMPLATE = """
你是一位专业的数据分析助手，你的回应内容取决于用户的请求内容。
你的目标是根据用户提供的CSV数据和问题，提供精确的分析结果，并以指定的JSON格式返回。

1. 对于文字回答的问题，按照这样的格式回答：
    {"answer": "<你的回复写在这里>"}
例如：
    {"answer": "订单量最高的产品ID是'MNWC-067'"}
 
2. 如果用户需要一个表格，按照这样的格式回答：
    {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

3. 如果用户的请求适合返回条形图，按照下面的格式回答：
    {"bar": {"columns": ["A", "B", "C", ...], "data": [21, 35, 78, ...]}}
    注意：bar键的值是一个字典，"columns"对应图表的X轴，"data"对应图表的Y轴数据。

4. 如果用户的请求适合返回折线图，按照下面的格式回答：
    {"line": {"columns": ["A", "B", "C", ...], "data": [21, 35, 78, ...]}}
    注意：line键的值是一个字典，"columns"对应图表的X轴，"data"对应图表的Y轴数据。
    
5. 如果用户的请求适合返回散点图，按照下面的格式回答：
    {"scatter": {"columns": ["A", "B", "C", ...], "data": [21, 35, 78, ...]}}
    注意：scatter键的值是一个字典，"columns"对应图表的X轴，"data"对应图表的Y轴数据。
    
注意：我们只支持三种类型的图表："bar", "line", "scatter"

请将所有输出作为**严格的JSON字符串**返回，请注意将"columns"列表和"data"列表中的所有字符串都用双引号包围。
例如：{"columns": ["Products", "Orders", ...], "data": [["423452Lio", 341, ...], ["423906Ypl", 368, ...], ...]}

请确保你的回复始终是一个有效的JSON字符串。如果无法生成有效数据或图表，请以文本形式说明原因。

你要处理的用户请求如下：
"""


def dataframe_agent(openai_api_key, df, query):
   try:
       # 初始化模型
       model = ChatOpenAI(model="gpt-3.5-turbo",
                          api_key=openai_api_key,
                          openai_api_base="https://api.aigc369.com/v1",
                          temperature=0) #让模型遵循ReAct框架

       # 创建Dataframe agent执行器
       agent_executor = create_pandas_dataframe_agent(
           llm=model,
           df=df,
           verbose=True, # 了解模型是如何思考的
           agent_executor_kwargs={"handle_parsing_errors": True}, #尽可能地让模型自行消化和处理错误，而不是让程序直接终止
           allow_dangerous_code=True  # 允许 Agent 执行 Python 代码，请谨慎使用
       )

       # 如果说我们只是想获得AI针对DataFrame的回答，我们可以直接把query传入agent的invoke方法。因为这种情况下，它返回的内容，我们会直接作为字符串展示。
       # 在这个项目里，前端需要知道下一步到底是把返回内容直接站展示为字符串，还是展示为表格，还是展示为图表
       # 一个解决办法是我们让agent返回一个字典，根据字典里的不同键来判断下一步的操作。比如说字典里面包含一个叫answer的键，说明我们要展示字符串，以此类推
       # 我们要把这些要求给agent说清楚
       # 不管响应格式被要求成啥样，AI返回的都是字符串。下一步，才是把它们解析为字典。所以，我们可以要求AI返回JSON字符串，因为解析JSON是相当容易的，有现成的方法

       prompt = PROMPT_TEMPLATE + query
       response = agent_executor.invoke({"input": prompt})

       # 尝试解析AI的响应，增加JSON解析的错误处理
       try:
           response_dic = json.loads(response["output"])
           return response_dic
       except json.JSONDecodeError as e:
           # 如果AI返回的不是有效的JSON，提示用户并建议重试或调整问题
           print(f"JSON解析错误：{e}，AI返回内容：{response['output']}")
           return {"answer": f"抱歉，AI返回的数据格式不正确，无法解析。请尝试调整问题或稍后重试。详细错误：{e}"}

   except openai.APIError as e:
       print(f"OpenAI API错误：{e}")
       return f"抱歉，OpenAI API 调用失败，错误信息：{e.message}。请检查您的API密钥或稍后重试。"
   except Exception as e:
       print(f"发生未知错误：{e}")
       return f"抱歉，发生未知错误：{e}，请联系管理员或稍后再试。"


