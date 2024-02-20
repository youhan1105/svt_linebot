from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction, TemplateSendMessage, CarouselTemplate, CarouselColumn, URIAction
from linebot.exceptions import InvalidSignatureError
from google.cloud import storage
import os
import random
import re
import emoji
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#region #串接憑證
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gs_credentials.json"
cred = credentials.Certificate("test-firebase-token.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://test-e2b8b-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
#endregion

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

#region #Linebot設定 
channel_access_token = 'mCJ2+jdUUJZ7gvYlTbhHFcs9MPyXn16iV/67s376Fif/XG5a4Mo++0mkcwn2opdG5ExcAcgygV67cGfvBaMO4+sKIyjkuehgmIK1UsZX1CDTZ1FhFjREv4Nr9Mt0Hh6EJ8yDYxrI2stTMfvgDbDnxwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler('a9e412bf3df519409feb6316871e750b')
#endregion

#region # Google Cloud Storage 設定
storage_client = storage.Client()
bucket_name = 'line-carat-hey-image'
blob_name = 'Database/svt-data-0219.json'
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(blob_name)
data = json.loads(blob.download_as_string())
#endregion

#region #Firebase資料
ref = db.reference('/')
fire_data = ref.get()
if fire_data is None:
    fire_data = {}
user_image_index = fire_data.get('user_image_index', {})
#endregion

#region #處理 Line Bot Webhook
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
#endregion

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    current_row_index = None
    new_image_index = None
    user_id = event.source.user_id
    user_input = event.message.text
    user_data = fire_data.get(user_id)

    if user_data is None:
        user_image_index = {}
        user_data = {'user_image_index': user_image_index}
        ref.child(user_id).set(user_data)
        print("user_data:", user_data)

    else:
        user_image_index = user_data.get('user_image_index', {})
        current_row_index = user_image_index[user_id]
        
        if user_image_index is None or not isinstance(user_image_index, dict):
            user_image_index = {}

    if user_input == str('抽'):
        image_urls = []
        random_row = random.choice(data)
        image_urls = random_row.get('圖片網址')  
        new_image_index = data.index(random_row)
        image_messages = [ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)]
    
        quick_reply_items = [
            QuickReplyButton(action=MessageAction(label='取得編號', text='取得編號')),
            QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
            QuickReplyButton(action=MessageAction(label='下一張', text='下一張')),
            QuickReplyButton(action=MessageAction(label='抽', text='抽'))
        ]
        quick_reply = QuickReply(items=quick_reply_items)
        for image_message in image_messages:
            image_message.quick_reply = quick_reply

        line_bot_api.reply_message(event.reply_token, image_messages)

    elif user_input == str('取得編號'):
        current_row_index = user_image_index[user_id]
        print("user_image_index:", user_image_index)
        print("current_row_index:", current_row_index)
        if user_image_index is not None and user_id in user_image_index and user_image_index[user_id] is not None:
            
            if current_row_index is not None and current_row_index < len(data):
                current_row = data[current_row_index]
                image_number = current_row.get('編號')
                image_name = current_row.get('中字')

                quick_reply_items = [
                    QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
                    QuickReplyButton(action=MessageAction(label='下一張', text='下一張')),
                    QuickReplyButton(action=MessageAction(label='抽', text='抽'))
                ]
                quick_reply = QuickReply(items=quick_reply_items)

                text_message = TextSendMessage(text=f"圖片編號為：\n【{image_number}】{image_name}", quick_reply=quick_reply)
                line_bot_api.reply_message(event.reply_token, text_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先抽圖片"))

    elif user_input == str("下一張"):
        if user_id in user_image_index:
            if current_row_index is not None:
                current_row_index += 1

                if current_row_index < len(data):
                    next_row = data[current_row_index]
                    next_image_urls = next_row.get('圖片網址')
                    new_image_index = current_row_index     
                    next_image_messages = [ImageSendMessage(original_content_url=next_image_urls, preview_image_url=next_image_urls)]
            
                    quick_reply_items = [
                        QuickReplyButton(action=MessageAction(label='取得編號', text='取得編號')),
                        QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
                        QuickReplyButton(action=MessageAction(label='下一張', text='下一張')),
                        QuickReplyButton(action=MessageAction(label='抽', text='抽'))
                    ]
                    quick_reply = QuickReply(items=quick_reply_items)

                    for next_image_message in next_image_messages:
                        next_image_message.quick_reply = quick_reply

                    line_bot_api.reply_message(event.reply_token, next_image_messages)

                else:

                    quick_reply_items = [
                        QuickReplyButton(action=MessageAction(label='取得編號', text='取得編號')),
                        QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
                        QuickReplyButton(action=MessageAction(label='抽', text='抽'))
                    ]
                    quick_reply = QuickReply(items=quick_reply_items)
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已經是最後一張圖片了"))

    elif user_input == str("上一張"):
        if user_id in user_image_index:
            if current_row_index is not None:
                current_row_index -= 1

                if current_row_index >= 0:
                    previous_row = data[current_row_index]
                    previous_image_urls = previous_row.get('圖片網址')
                    new_image_index = current_row_index 
                    previous_image_messages = [ImageSendMessage(original_content_url=previous_image_urls, preview_image_url=previous_image_urls)]
            
                    quick_reply_items = [
                        QuickReplyButton(action=MessageAction(label='取得編號', text='取得編號')),
                        QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
                        QuickReplyButton(action=MessageAction(label='下一張', text='下一張')),
                        QuickReplyButton(action=MessageAction(label='抽', text='抽'))
                    ]
                    quick_reply = QuickReply(items=quick_reply_items)

                    for previous_image_message in previous_image_messages:
                        previous_image_message.quick_reply = quick_reply            
            
                    line_bot_api.reply_message(event.reply_token, previous_image_messages)
            
                else:
                    quick_reply_items = [
                        QuickReplyButton(action=MessageAction(label='抽', text='抽'))
                    ]
                    quick_reply = QuickReply(items=quick_reply_items)
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已經是第一張圖片了"))

    ref.child(user_id).update({'user_image_index': new_image_index})

if __name__ == "__main__":
    app.run()
