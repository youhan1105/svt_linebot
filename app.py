from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage,TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
from linebot.exceptions import InvalidSignatureError
from oauth2client.service_account import ServiceAccountCredentials

import gspread
import os
import random
import re

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

#region #Linebot設定 
channel_access_token = 'mCJ2+jdUUJZ7gvYlTbhHFcs9MPyXn16iV/67s376Fif/XG5a4Mo++0mkcwn2opdG5ExcAcgygV67cGfvBaMO4+sKIyjkuehgmIK1UsZX1CDTZ1FhFjREv4Nr9Mt0Hh6EJ8yDYxrI2stTMfvgDbDnxwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler('a9e412bf3df519409feb6316871e750b')
#endregion

#region #Googlesheet串接
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creditials = ServiceAccountCredentials.from_json_keyfile_name('gs_credentials.json', scopes=scope)
client = gspread.authorize(creditials)
sheet = client.open("First sheet").sheet1
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

#region #全域變數用於追蹤已發送圖片的索引
global current_row_index
current_row_index = None
data = None
data = sheet.get_all_records() # 取得 Google Sheets 所有資料
#endregion

#主程式 
@handler.add(MessageEvent, message=TextMessage) #處理收到的訊息事件
def handle_message(event):
    global current_row_index
    user_input = event.message.text

emoji_mapping = {
    "🍒": "01",
    "🐰": "02",
    "🦌": "03",
    "😺": "04",
    "🐯": "05",
    "🐹": "05",
    "🐈‍⬛": "06",
    "🍚": "07",
    "🎱": "08",
    "🐸": "08",
    "🐶": "09",
    "⚔️": "10",
    "🍕": "10",
    "🍊": "11",
    "🐻": "11",
    "🐻‍❄️": "12",
    "🎧": "12",
    "🦖": "13",
    "🦦": "13",
}
        
    if user_input == str('抽'):
        
        image_urls = []
        
        #隨機選擇一列資料
        random_row = random.choice(data)  
        image_urls = random_row.get('圖片網址')  #取得圖片網址欄位的文字內容
        current_row_index = data.index(random_row)        
        image_messages = [ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)]
        
        #製作按紐
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
        if current_row_index is not None:
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
        if current_row_index is not None:
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

    elif re.match(r'^[A-Za-z]', user_input) and len(user_input) == 8:  # 檢查是否為八字元且為英文開頭
        image_urls = []

        # 尋找符合的圖片編號      
        for row_index,row in enumerate(data):
            if str(user_input) in row[str('編號')]:
                image_urls.append(row['圖片網址'])
                current_row_index = row_index

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

    elif re.match(r'^[A-Za-z]\d{3}$', user_input): # 搜尋集數，得到整集的圖
        matched_data = []
        for row in data:
            if str(user_input) in row[str('集數')]:
                matched_data.append(f"【{row[str('編號')]}】 {row[str('中字')]}")
        
        if matched_data:
            reply_message = "\n".join(matched_data)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        
        else:
            reply_message = "尚未有此集的資料"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

    elif user_input in emoji_mapping: # 抽emoji
        search_condition = emoji_mapping[user_input]

        # 搜尋 google sheet 中 "成員" 欄位內容為搜尋條件的橫列
        matched_data = []
        image_urls = []
        for row in data:
                # 檢查 "成員" 欄位的值是否可迭代
            if hasattr(row[str('成員')], '__iter__'):
                if str(search_condition) in row[str('成員')]:
                    matched_data.append(row)
            else:
                # 如果 "成員" 欄位的值不可迭代，將其轉換為字符串再進行比較
                if str(search_condition) == str(row[str('成員')]):
                    matched_data.append(row)

        if matched_data:
            # 隨機選擇一列資料
            random_row = random.choice(matched_data)
            image_urls = random_row.get('圖片網址')  # 取得圖片網址欄位的文字內容
            current_row_index = data.index(random_row)
            image_messages = [ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)]

        # 製作按鈕
            quick_reply_items = [
                QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
                QuickReplyButton(action=MessageAction(label='下一張', text='下一張')),
                QuickReplyButton(action=MessageAction(label='抽', text='抽')),
                QuickReplyButton(action=MessageAction(label=user_input, text=user_input))
            ]

            quick_reply = QuickReply(items=quick_reply_items)
            
            for image_message in image_messages:
                image_message.quick_reply = quick_reply


            line_bot_api.reply_message(event.reply_token, image_messages)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無符合條件的emoji"))

    else:  #任意文字查詢
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


if __name__ == "__main__":
    app.run()
