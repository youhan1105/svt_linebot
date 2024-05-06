from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction, TemplateSendMessage, CarouselTemplate, CarouselColumn, URIAction
from linebot.exceptions import InvalidSignatureError
from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials

import gspread
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

#region #Googlesheet串接
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creditials = ServiceAccountCredentials.from_json_keyfile_name('gs_credentials.json', scopes=scope)
client = gspread.authorize(creditials)
sheet = client.open("SVT-linebot").sheet1
new_image_index = 0
data = None
data = sheet.get_all_records() 
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
        emoji.emojize("💰"): "工作",
	    emoji.emojize("❤️"): "誇誇",
	    emoji.emojize("❓"): "問答",

    }
 
    user_input_to_reply_message = {
    "抽圖/搜尋關鍵字/取得圖片": [
        "🎲隨機圖片：\n輸入「抽」，獲得隨機圖片\n\n📸發送圖片：\n輸入編號，獲得指定圖片\n例如輸入：G1140002\n\n🔍搜尋圖片：\n直接輸入關鍵字，出現包含此關鍵字的所有圖片編碼",
        "🔢整集列表：\n參考「圖庫收錄集數」清單，輸入「1英文+3數字」，獲得該集圖片清單\n\n選單 》「圖庫相關」\n》點選「圖庫收錄集數」\n》查找特定集數\n》輸入該集的編碼（1英文+3數字）\n》獲得該集圖片清單"
    ],
    "取得編號/上一張/下一張": [
        "📄取得編碼：\n得知目前圖片的編號與關鍵字\n方便下一次搜尋此圖片，或者藉由編號得知圖片出處\n\n⬆️上一張：\n獲得上一編號的圖片。\n同一集內容、同一位成員，圖片編號會連續 \n\n⬇️下一張：\n獲得下一編號的圖片。\n同一集內容、同一位成員，圖片編號會連續"
    ],
    "抽特定成員": [
        "🍒抽指定成員：\n\n輸入成員各自的emoji，獲得該成員隨機圖片\n\n每位成員所對應emoji，可能不只一個"
    ],
    "主題抽圖": [
        "💰好想下班：\n輸入「💰」，獲得打工人心聲迷因",
        "❤️愛的誇誇：\n輸入「❤️」，獲得正向句子的迷因",
        "❓人生光明燈：\n輸入「❓」，隨機獲得「肯定」或者「否定」迷因，以此幫助有選擇障礙的你！\n p.s.建議詢問是非題"
    ],
    "成員emoji列表": [
        "S.COUPS：🍒,🦁\n淨漢：🐰,😇,👼🏻,👼\nJoshua：🦌\nJun：🐱\nHoshi：🐯,🐹\n圓佑：🐈‍⬛,🎮,👓\nWOOZI：🍚🍑\nTHE 8：🎱,🐸\n珉奎：🐶,🌻\nDK：⚔️,🍕\n勝寛：🍊,🐻\nVernon：🐻‍❄️,🎧\nDino：🦖,🦦"
    ],
    "想知道每張圖的Going集數": [
        "取得圖片後，點選下方「取得編號」按鈕。\n編號最前面的「英文字母+三位數字」即為圖片出處。\n\n需對照👉圖庫集數總覽\n\n下方選單→圖庫相關→集數總覽"
    ],
    "「取得編號」的作用？": [
        "得知目前圖片的編號與關鍵字。\n方便下一次搜尋此圖片，或者藉由編號得知圖片出處。"
    ],
    "編碼的數字意義": [
        "可分為：\n「開頭1英文+前面3數字」：系列與集數\n「中間2數字」：成員\n「最後2數字」：第幾張圖\n\n詳情參考👉圖庫編碼原則\n\n下方選單→圖庫相關→編碼原則"
    ],
    "想看到全部的圖": [
        "目前想讓使用者體驗隨機抽圖的樂趣😆\n\n之後會將圖片公開於雲端硬碟，\n請再等等！Thanks！"
    ],
    "克拉嘿可以傳圖片嗎？": [
        "可以！你可以傳圖片給機器人。\n\n但並不會觸發任何功能，接下來抽出的圖也不會有關聯🤣"
    ],
    "電腦可以使用克拉嘿嗎？": [
        "可以！電腦版也可以使用～\n\n但電腦版不會出現下方的快速回覆功能，需要手動輸入「抽」"
    ],
    "其他聯絡": [
        "其他事項聯絡我，請寄email!",
        "Line.Carat.Hey@gmail.com"
    ],
    "主題抽圖：愛的誇誇❤️": [
        "❤️愛的誇誇：\n輸入「❤️」，獲得正向句子的迷因"
    ],
    "主題抽圖： 人生光明燈❓": [
        "輸入「❓」，隨機獲得「肯定」或者「否定」迷因，以此幫助有選擇障礙的你！\n p.s.建議詢問是非題"
    ], 
    "雲端圖庫": [
        "此機器人與圖庫皆為無償提供><\n若想與朋友分享圖庫：\n⭕️請邀請他們加入此帳號好友 \n❌請勿直接在社群媒體上分享下方連結",
        "https://drive.google.com/drive/folders/1DjWUkrqe-W-6_TLMyT8Yx95okt3lRcvg?usp=share_link"    
        ], 

    }

    global current_row_index
    global new_image_index
    user_id = event.source.user_id
    user_input = event.message.text
	
    #Firebase資料
    ref = db.reference('/')
    user_ref = ref.child(user_id)
    user_data = {}
    user_data = user_ref.get()
    user_image_index = 0

    if user_data is None:
        user_data = {}
        user_image_index = 0
        user_data = {'user_image_index': user_image_index}
        ref.child(user_id).set(user_data)

    if not isinstance(user_image_index, int):
        user_image_index = 0

    if 'silent_mode' not in user_data:
        user_data['silent_mode'] = 0

    user_image_index = user_data.get('user_image_index', 0 )
    
    
    current_row_index = user_image_index
	
    if user_input == str("完整功能"):
        carousel_template = CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-new.jpg",
                    text="24/05 最新功能",
                    actions=[
                        MessageAction(label="主題抽圖：愛的誇誇❤️", text="主題抽圖：愛的誇誇❤️"),
                        MessageAction(label="主題抽圖： 人生光明燈❓", text="主題抽圖： 人生光明燈❓")
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-basic.jpg",
                    text="👀新加入的克拉看這裡！",
                    actions=[
                        MessageAction(label="抽圖/搜尋關鍵字/取得圖片", text="抽圖/搜尋關鍵字/取得圖片"),
                        MessageAction(label="取得編號/上一張/下一張", text="取得編號/上一張/下一張")
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-adv.jpg",
                    text="💖如何抽出更符合心意的圖？",
                    actions=[
                        MessageAction(label="抽特定成員", text="抽特定成員"),
                        MessageAction(label="主題抽圖", text="主題抽圖")                        
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-qa.jpg",
                    text="❓疑難雜症解決專區",
                    actions=[
                        MessageAction(label="成員emoji列表", text="成員emoji列表"),
                        MessageAction(label="點這裡看更多⋯", text="更多常見問題")                           
                    ]
                )
            ]
        )
        carousel_message = TemplateSendMessage(alt_text='圖文選單', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, carousel_message)
    
    elif user_input == str("更多常見問題"):
        carousel_template = CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-qa2.jpg",
                    text="常見問題看這邊",
                    actions=[
                        MessageAction(label="想知道每張圖的Going集數", text="想知道每張圖的Going集數"),
                        MessageAction(label="「取得編號」的作用？", text="「取得編號」的作用？"),
                        MessageAction(label="編碼的數字意義", text="編碼的數字意義"),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-qa2.jpg",
                    text="常見問題看這邊",
                    actions=[
                        MessageAction(label="想看到全部的圖", text="想看到全部的圖"),
                        MessageAction(label="克拉嘿可以傳圖片嗎？", text="克拉嘿可以傳圖片嗎？"),
                        MessageAction(label="電腦可以使用克拉嘿嗎？", text="電腦可以使用克拉嘿嗎？")
                    ]
                )
            ]
        )
        carousel_message = TemplateSendMessage(alt_text='圖文選單', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, carousel_message)

    elif user_input == str("聯絡作者"):
        carousel_template = CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-contact.jpg",
                    text="歡迎與我分享使用心得❤️",                    
                    actions=[
                            URIAction(label="錯誤回報", uri="https://forms.gle/YhhYvoYomCXGbwoq5"),
                            URIAction(label="許願池", uri="https://forms.gle/endRDk4AWcAHvLVH6"),
                            MessageAction(label="其他聯絡", text="其他聯絡")
                    ]
                )
            ]
        )
        carousel_message = TemplateSendMessage(alt_text='圖文選單', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, carousel_message)

    elif user_input == str("圖庫相關"):
        carousel_template = CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-ep.jpg",
                    text="🔠已收錄的集數與對應編號",
                    actions=[
                            URIAction(label="圖庫收錄集數", uri="https://linecarathey.wixsite.com/line-carat-hey/episode")
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-num.jpg",
                    text="📝系列+集數+成員+第幾張",
                    actions=[
                            URIAction(label="編碼說明", uri="https://linecarathey.wixsite.com/line-carat-hey/rules")
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://storage.googleapis.com/seventeen-image/linebot-image/many-download.jpg",
                    text="☁️收錄圖片一次看！",
                    actions=[
                            MessageAction(label="雲端圖庫", text="雲端圖庫")
                    ]
                )
                
            ]
        )
        carousel_message = TemplateSendMessage(alt_text='圖文選單', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, carousel_message)


    elif user_input in user_input_to_reply_message:
        reply_messages = user_input_to_reply_message[user_input]
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=message) for message in reply_messages])

    elif user_input == str('抽'):
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

    elif user_input == str("下一張"):
        if current_row_index is not None:
            current_row_index += 1

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

    elif user_input == str("上一張"):
        if current_row_index is not None:
            current_row_index -= 1

            if current_row_index >= 0:
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

            new_image_index = current_row_index
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
        for row in data:
           # 檢查 "成員" 欄位的值是否可迭代
            if hasattr(row[str('主題')], '__iter__'):
                if str(search_condition) in row[str('主題')]:
                    matched_data.append(row)
            else:
                # 如果 "成員" 欄位的值不可迭代，將其轉換為字符串再進行比較
                if str(search_condition) == str(row[str('主題')]):
                    matched_data.append(row)

        if matched_data:
            # 隨機選擇一列資料
            random_row = random.choice(matched_data)
            image_urls = random_row.get('圖片網址') 
            new_image_index = data.index(random_row)

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
            if user_data['silent_mode'] == 0:
                reply_message = "無符合的資料"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

    user_ref.update(user_data)

if __name__ == "__main__":
    app.run()
