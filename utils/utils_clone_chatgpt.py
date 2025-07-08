from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
import openai  #导入openai库，以便捕获其特定的异常


# 定义获得AI模型回答的函数
    #为了让模型可以获取之前和用户的对话内容，我们需要传入记忆，而不是在函数内部去初始化记忆。
    #因为如果记忆是在函数内部被创建的话，对话列表是空的，模型仍然无法得到之前的对话内容。所以记忆是从外部传入的
    #初始化模型这一步放在前端页面中
def get_chat_response(openai_api_key, prompt, memory):
    try:
        # 使用OpenAI的API密钥初始化模型
        model = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key, openai_api_base="https://api.aigc369.com/v1")
        # 创建一个对话链，将模型和记忆绑定在一起
        chain = ConversationChain(llm=model, memory=memory)
        result = chain.invoke({"input": prompt})
        return result["response"]
    except openai.APIError as e:
        #捕获OpenAI API错误，例如API密钥无效、余额不足、请求频率限制等
        print(f"OpenAI API 错误：{e}")  #开发者看的，用于调试和记录内部错误。
        return f"抱歉，Open AI API 调用失败。错误信息：{e.message}。请检查您的API密钥或稍后再试"  #用户看的，用于在前端界面显示友好的错误提示。
    except Exception as e:
        # 捕获其他未知错误
        print(f"发生未知错误：{e}")
        return f"抱歉，发生未知错误：{e}。请联系管理员或稍后再试。"




