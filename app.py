import os
import google.generativeai as genai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)

# 設定 LINE Bot 相關參數
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

# 設定 Google Gemini API Key
genai.configure(api_key=os.environ['GOOGLE_GEMINI_API_KEY'])

# 初始化 Gemini 模型
model = genai.GenerativeModel('gemini-pro')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 取得使用者輸入的文字
    user_input = event.message.text

    # 使用 Gemini 模型產生回覆
    response = model.generate_text(
        prompt=user_input,
        max_output_tokens=256,
        temperature=0.7
    )

    # 在回覆前加上提示訊息
    reply_message = "以下回覆是使用 Gemini 模型回復:\n\n" + response.text

    # 回覆給使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
