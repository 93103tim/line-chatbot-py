from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

from chatbot_chain import get_chatbot_chain

import tempfile
import datetime
import openai
import time
import traceback
import os
import google.generativeai as genai

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))

# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

#Gemini api
genai.configure(api_key=os.environ['GOOGLE_GEMINI_API_TOKEN'])
model = genai.GenerativeModel('gemini-1.5-flash')

def GPT_response(text):
    # 接收回應
    response = model.generate_content(text)
    print("已收到回應訊息"+response.text)
    
    return response.text


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
    
    GPT_answer = GPT_response(msg)
    print(GPT_answer)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
        

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
