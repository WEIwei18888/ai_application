from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain

import os
import  tempfile
import openai
from pypdf.errors import PdfReadError # 导入PdfReadError，用于捕获PDF读取错误



def qa_agent(openai_api_key, memory, uploaded_file, question):
    try:
        # 初始化模型
        model = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key, openai_api_base="https://api.aigc369.com/v1")

        # 创建临时文件，解决文件路径的问题
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # 写入上传的内容
            temp_file.write(uploaded_file.getvalue())  # 从 Streamlit 上传组件获取的文件对象中读取二进制内容。
            temp_file_path = temp_file.name

        # 构建pdf文档加载器
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()

        # 检查PDF是否提取到任何文档内容
        if not documents:
            return "抱歉，无法从上传的PDF文件中提取任何文本内容。这可能是因为PDF文件为空、受损或不包含可读文本。请尝试上传一个有效的PDF文件。"

        # 构建文档分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=80,
            separators=["\n\n", "\n", "。", "！", "？"]
        )
        # 分割读取的文档
        texts = text_splitter.split_documents(documents)

        # 检查文本分割后是否产生任何有效片段
        if not texts:
            return "抱歉，文本分割后未产生任何有效内容。这可能是由于PDF内容过少或其格式复杂导致无法有效分割。请检查您的PDF文件内容。"

        # 构建嵌入模型
        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small",
                                            openai_api_key=openai_api_key,
                                            openai_api_base="https://api.aigc369.com/v1")

        # 构建向量数据库
        db = FAISS.from_documents(texts, embeddings_model)
        # 构建检索器
        retriever = db.as_retriever()

        # 构建检索增强对话链
        qa = ConversationalRetrievalChain.from_llm(
            llm=model,
            retriever=retriever,
            memory=memory,
            return_source_documents=True
        )

        # 使用问答链获取答案
        # 它传入一个字典，字典里面两个键"chat_history"、"question"
        response = qa.invoke({"chat_history": memory, "question": question})  # 返回结果是一个字典。"chat_history"\ "question"\ "answer"

        return response #居然写代码写掉了

    except openai.APIError as e:
        # 捕获OpenAI API错误，例如API密钥无效、余额不足、请求频率限制等
        print(f"OpenAI API错误：{e}")
        return f"抱歉 OpenAI API 调用失败。错误信息：{e.message}。请检查您的API密钥或稍后再试。"
    except PdfReadError as e:  # 新增：捕获PDF读取特有错误
        print(f"PDF读取错误：{e}")
        return f"抱歉，读取PDF文件时发生错误：{e}。这通常是由于PDF文件损坏、格式不正确或被加密导致无法读取。请尝试上传一个有效的PDF文件。"
    except Exception as e:
        print(f"发生未知错误：{e}")
        return f"抱歉，发生未知错误：{e}。请联系管理员或稍后再试。"

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"临时文件已删除：{temp_file_path}")