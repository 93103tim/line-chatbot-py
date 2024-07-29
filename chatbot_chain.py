import os
#from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders.pdf import PyMuPDFLoader
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import google.generativeai as genai

def get_chatbot_chain():
    openai_api_key = os.environ["OPENAI_API_KEY"]
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    #初始化Gemini模型
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    #載入檔案
    #loader = CSVLoader(file_path="/content/faq.csv")
    loader = PyMuPDFLoader(file_path="/content/Go Shape健康美學（論文）.pdf")
    documents = loader.load()

    #使用Faiss vectordb儲存由OpenaiEmbedding過的內容
    vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())

    #儲存記憶
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(llm=model,
                            retriever=vectorstore.as_retriever(),
                            memory=memory)
    return chain
