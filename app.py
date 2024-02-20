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
json_data = json.loads(blob.download_as_string())
#endregion

#region #全域變數用於追蹤已發送圖片的索引
new_image_index = 0
data = None
data = json_data 
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
    global current_row_index
    global new_image_index
    user_id = event.source.user_id
    user_input = event.message.text

    #Firebase資料
    ref = db.reference('/')
    fire_data = ref.get()

    if fire_data is None:
        fire_data = {}
    
    user_data = fire_data.get(user_id, {})
    user_image_index = user_data.get('user_image_index', 0 )
    current_row_index = user_image_index
    print('user_data',user_data)
    print('current_row_index-0:',current_row_index)

    if user_id not in user_data:
        user_image_index = 0
        print('not in')

        if not user_data:
            user_data = {'user_image_index': user_image_index}
            ref.child(user_id).set(user_data)
            print('set')

        elif user_image_index is None or not isinstance(user_image_index, int):
            user_image_index = user_data.get('user_image_index', 0 )

    elif user_input == str('抽'):
        image_urls = []
        random_row = random.choice(data)  
        image_urls = random_row.get('圖片網址')  
        new_image_index = data.index(random_row) 
        image_messages = [ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)]
        print('current_row_index-ran:',current_row_index)
    
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
        print('current_row_index-3:',current_row_index)
        if current_row_index is not None:
            if current_row_index < len(data):
                current_row = data[current_row_index]
                image_number = current_row.get('編號')
                image_name = current_row.get('中字')

        
                quick_reply_items = [
                    QuickReplyButton(action=MessageAction(label='上一張', text='上一張')),
                    QuickReplyButton(action=MessageAction(label='下一張', text='下一張')),
                    QuickReplyButton(action=MessageAction(label='抽', text='抽'))
                ]
                quick_reply = QuickReply(items=quick_reply_items)

                # 建立回覆訊息，包含 Quick Reply 按鈕
                text_message = TextSendMessage(text=f"圖片編號為：\n【{image_number}】{image_name}", quick_reply=quick_reply)

        
                line_bot_api.reply_message(event.reply_token, text_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先抽圖片"))
            print('current_row_index-4:',current_row_index)

    elif user_input == str("下一張"):
        print('current_row_index-5:',current_row_index)
        if user_id in user_image_index:
            current_row_index = user_image_index[user_id]
            print('current_row_index-6:',current_row_index)
            if current_row_index is not None:
                current_row_index += 1
                print('current_row_index-7:',current_row_index)

                if current_row_index < len(data):
                    next_row = data[current_row_index]
                    next_image_urls = next_row.get('圖片網址')     
                    current_row_index = data.index(next_row) 
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

    ref.child(user_id).update({'user_image_index': new_image_index})

if __name__ == "__main__":
    app.run()





    emoji_mapping = {
        emoji.emojize("🍒"): "1",
        emoji.emojize("🦁"): "1",   
        emoji.emojize("🐰"): "2",
        emoji.emojize("😇"): "2",
        emoji.emojize("👼🏻"): "2",
        emoji.emojize("👼"): "2",
        emoji.emojize("🦌"): "3",
        emoji.emojize("🐱"): "4",
        emoji.emojize("🐯"): "5",
        emoji.emojize("🐹"): "5",
        emoji.emojize("🐈‍⬛"): "6",
        emoji.emojize("🎮"): "6",
        emoji.emojize("👓"): "6",        
        emoji.emojize("🍚"): "7",
        emoji.emojize("🍑"): "7",
        emoji.emojize("🎱"): "8",
        emoji.emojize("🐸"): "8",
        emoji.emojize("🐶"): "9",
        emoji.emojize("🌻"): "9",        
        emoji.emojize("⚔️"): "10",
        emoji.emojize("🍕"): "10",
        emoji.emojize("🍊"): "11",
        emoji.emojize("🐻"): "11",
        emoji.emojize("🐻‍❄️"): "12",
        emoji.emojize("🎧"): "12",
        emoji.emojize("🦖"): "13",
        emoji.emojize("🦦"): "13",
    }
        
    if user_input == str("完整功能"):
        carousel_template = CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/line-carat-hey-image/image/01.jpg",
                    text="本機器人詳細功能說明",
                    actions=[
                        MessageAction(label="抽圖/搜尋關鍵字/特定圖片", text="抽圖/搜尋關鍵字/特定圖片")
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/line-carat-hey-image/image/02.jpg",
                    text="已收錄的集數清單及編號",
                    actions=[
                        URIAction(label="圖庫收錄集數", uri="https://linecarathey.wixsite.com/line-carat-hey/episode")
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/line-carat-hey-image/image/03.jpg",
                    text="系列+集數+成員+第幾張",
                    actions=[
                        URIAction(label="編碼說明", uri="https://linecarathey.wixsite.com/line-carat-hey/rules")
                    ]
                )
            ]
        )
        carousel_message = TemplateSendMessage(alt_text='Carousel template', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, carousel_message)

    elif user_input == str("抽圖/搜尋關鍵字/特定圖片"):
        reply_message1 = "🎲隨機圖片：\n輸入「抽」，獲得隨機圖片\n\n🍒抽指定成員：\n輸入成員各自的emoji，獲得該成員隨機圖片\n\n📸發送圖片：\n輸入編號（不含括號），獲得指定圖片\n如：G1140002\n\n🔍搜尋圖片：\n直接輸入關鍵字，出現包含此關鍵字的所有圖片編碼"        
        reply_message2 = "🔢整集列表：\n參考「圖庫收錄集數」清單，輸入「1英文+3數字」，獲得該集圖片清單\n\n選單 》「完整功能」\n》點選「圖庫收錄集數」\n》查找特定集數\n》輸入該集的編碼（1英文+3數字）\n》獲得該集圖片清單"                
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply_message1),TextSendMessage(text=reply_message2)])

    elif user_input == str("圖庫收錄集數"):
        carousel_template = CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url="https://i.imgur.com/A3XvDnd.jpg",
                    text="已收錄集數清單及編號",
                    actions=[
                        URIAction(label="已收錄集數", uri="https://linecarathey.wixsite.com/line-carat-hey/episode")
                    ]
                )
            ]
        )
        carousel_message = TemplateSendMessage(alt_text='Carousel template', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, carousel_message)

    elif user_input == str("上一張"):
        user_id = event.source.user_id
        if user_id in user_image_index:
            current_row_index = user_image_index[user_id]
            if current_row_index is not None:
                current_row_index -= 1

                if current_row_index >= 0:
                    previous_row = data[current_row_index]
                    previous_image_urls = previous_row.get('圖片網址')
                    current_row_index = data.index(previous_row) 
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

    elif re.match(r'^[A-Za-z]', user_input) and len(user_input) == 8:  # 檢查是否為八字元且為英文開頭
        image_urls = []

        # 尋找符合的圖片編號      
        for row_index,row in enumerate(data):
            if str(user_input) in row[str('編號')]:
                image_urls.append(row['圖片網址'])
                current_row_index = row_index

		# 如果找到符合的圖片網址		   
        if image_urls:  

            user_id = event.source.user_id
            user_image_index[user_id] = current_row_index

            image_messages = [ImageSendMessage(original_content_url=url, preview_image_url=url) for url in image_urls]
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
        
    
        else:  
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無符合的圖片編號"))

    elif re.match(r'^[A-Za-z]\d{3}$', user_input): # 搜尋集數，得到整集的圖
        matched_data = []
        for row in data:
            if str(user_input) in row[str('集數')]:
                matched_data.append(f"【{row[str('編號')]}】 {row[str('中字')]}")
        
        if matched_data:
            reply_message = "【Gxxx13xx】此數為成員編號\n＊輸入編號時請去掉括號＊\n\n"
            reply_message += "\n".join(matched_data)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        
        else:
            reply_message = "尚未有此集的資料"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

    elif user_input in emoji_mapping: # 抽emoji
        search_condition = emoji.emojize(emoji_mapping[user_input])

        # 搜尋欄位內容為搜尋條件的橫列
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
            image_urls = random_row.get('圖片網址') 
            current_row_index = data.index(random_row)

            user_id = event.source.user_id
            user_image_index[user_id] = current_row_index

            image_messages = [ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)]

            quick_reply_items = [
                QuickReplyButton(action=MessageAction(label='取得編號', text='取得編號')),
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

    
        for row in data:
            if str(user_input) in row[str('中字')]:
                matched_data.append(f"【{row[str('編號')]}】 {row[str('中字')]}")
    
    
        if matched_data:
            reply_message = "【Gxxx13xx】此數為成員編號\n＊輸入編號時請去掉括號＊\n\n"
            reply_message += "\n".join(matched_data)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        else:
            reply_message = "無符合的資料"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
