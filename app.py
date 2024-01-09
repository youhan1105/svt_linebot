from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage,TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
from linebot.exceptions import InvalidSignatureError
from oauth2client.service_account import ServiceAccountCredentials

import gspread
import os
import random

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

#Linebot設定
channel_access_token = 'mCJ2+jdUUJZ7gvYlTbhHFcs9MPyXn16iV/67s376Fif/XG5a4Mo++0mkcwn2opdG5ExcAcgygV67cGfvBaMO4+sKIyjkuehgmIK1UsZX1CDTZ1FhFjREv4Nr9Mt0Hh6EJ8yDYxrI2stTMfvgDbDnxwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler('a9e412bf3df519409feb6316871e750b')

# Googlesheet串接
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creditials = ServiceAccountCredentials.from_json_keyfile_name('gs_credentials.json', scopes=scope)
client = gspread.authorize(creditials)
sheet = client.open("First sheet").sheet1

# 全域變數用於追蹤已發送圖片的索引
global current_row_index
data = sheet.get_all_records()# 取得 Google Sheets 所有資料

# 處理收到的訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
        
    if user_input == str("抽"):
        image_urls = []
        
        # 隨機選擇一列資料
        random_row = random.choice(data)  
        image_urls = random_row.get('圖片網址')  # 取得圖片網址欄位的文字內容
        current_row_index = data.index(random_row)        
        image_messages = [ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)]
        
        quick_reply_items = [
            QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
            QuickReplyButton(action=MessageAction(label='下一張', text='下一張')),
            QuickReplyButton(action=MessageAction(label='抽', text='抽'))
        ]
        quick_reply = QuickReply(items=quick_reply_items)

        for image_message in image_messages:
            image_message.quick_reply = quick_reply

        line_bot_api.reply_message(event.reply_token, image_messages)

    elif user_input == str("下一張"):
        current_row_index += 1
        if current_row_index < len(data):
            next_row = data[current_row_index]
            next_image_urls = next_row.get('圖片網址')     
            current_row_index = data.index(next_row)   
            next_image_messages = [ImageSendMessage(original_content_url=next_image_urls, preview_image_url=next_image_urls)]
            
            quick_reply_items = [
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
                QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
                QuickReplyButton(action=MessageAction(label='抽', text='抽'))
            ]
            quick_reply = QuickReply(items=quick_reply_items)

            for next_image_message in next_image_messages:
                next_image_message.quick_reply = quick_reply     

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已經是最後一張圖片了"))

    elif user_input == str("上一張"):
        current_row_index -= 1
        if current_row_index >= 0:
            previous_row = data[current_row_index]
            previous_image_urls = previous_row.get('圖片網址')
            current_row_index = data.index(previous_row) 
            previous_image_messages = [ImageSendMessage(original_content_url=previous_image_urls, preview_image_url=previous_image_urls)]
            
            quick_reply_items = [
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
                QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
                QuickReplyButton(action=MessageAction(label='抽', text='抽'))
            ]
            quick_reply = QuickReply(items=quick_reply_items)

            for previous_image_message in previous_image_messages:
                previous_image_message.quick_reply = quick_reply     

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已經是第一張圖片了"))

    elif len(user_input) == 8 and user_input.startswith('G'):  # 檢查是否為七碼數字且為G開頭
        image_urls = []

        # 尋找符合的圖片編號      
        for row in data:
            if str(user_input) in row[str('編號')]:
                image_urls.append(row['圖片網址'])
                current_row = row

		# 如果找到符合的圖片網址		   
        if image_urls:  
            image_messages = [ImageSendMessage(original_content_url=url, preview_image_url=url) for url in image_urls]
            quick_reply_items = [
                QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
                QuickReplyButton(action=MessageAction(label='下一張', text='下一張')),
                QuickReplyButton(action=MessageAction(label='抽', text='抽'))
            ]
            quick_reply = QuickReply(items=quick_reply_items)

            for image_message in image_messages:
                image_message.quick_reply = quick_reply
            
            line_bot_api.reply_message(event.reply_token, image_messages)
        
        # 如果沒有符合的圖片編號
        else:  
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無符合的圖片編號"))


    # 如果使用者輸入的是任意文字
    else:
        matched_data = []

        # 在 Google Sheets 中搜尋符合的圖片編號和圖片名稱
        for row in data:
            if str(user_input) in row[str('中字')]:
                matched_data.append(f"【{row[str('編號')]}】 {row[str('中字')]}")
    
        # 回覆符合條件的資訊給使用者
        if matched_data:
            reply_message = "\n".join(matched_data)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        else:
            reply_message = "無符合的資料"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
			
# 處理 Line Bot Webhook
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

if __name__ == "__main__":
    app.run()
