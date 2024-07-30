import os
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.document_loaders.pdf import PyMuPDFLoader
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

openai_api_key = os.getenv("OPENAI_API_KEY")#Openai Api Key
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))# Channel Access Token
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))# Channel Secret

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

def get_chatbot_chain(msg):
    #載入檔案
    loader = PyMuPDFLoader(file_path="https://reg.ttu.edu.tw/var/file/32/1032/attach/32/pta_26621_295944_06457.pdf")
    documents = loader.load()

    #使用Faiss vectordb儲存由OpenaiEmbedding過的內容
    vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings(api_key=openai_api_key))

    #儲存記憶
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(api_key=openai_api_key),
                            retriever=vectorstore.as_retriever(),
                            memory=memory)
    
    return chain.invoke(msg)

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    print(body)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text

    line_bot_api.reply_message(event.reply_token, TextSendMessage(get_chatbot_chain(msg)))
        

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
