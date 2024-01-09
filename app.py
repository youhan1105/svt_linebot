from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage,TextSendMessage, ImageSendMessage
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

#Linebot設定
channel_access_token = 'mCJ2+jdUUJZ7gvYlTbhHFcs9MPyXn16iV/67s376Fif/XG5a4Mo++0mkcwn2opdG5ExcAcgygV67cGfvBaMO4+sKIyjkuehgmIK1UsZX1CDTZ1FhFjREv4Nr9Mt0Hh6EJ8yDYxrI2stTMfvgDbDnxwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler('a9e412bf3df519409feb6316871e750b')

#Googlesheet串接
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

creditials = ServiceAccountCredentials.from_json_keyfile_name('gs_credentials.json', scope)
client = gspread.authorize(creditials)

#建立新的試算表後分享給自己
#sheet = client.create("First sheet")
#sheet.share('claire60320@gmail.com',perm_type='user',role='writer')

#本地檔案寫入Googlesheet
#sheet= client.open("First sheet").sheet1
#df = pd.read_csv('goingsvt.csv')
#sheet.update([df.columns.values.tolist()] + df.values.tolist())

# 處理收到的訊息事件
def handle_message(event):
    user_input = event.message.text
    
    # 從 Google Sheets 中讀取「中字」欄位資料
    data = sheet.get_all_records()
    matched_data = []
    for row in data:
        if str(user_input) in row['中字']:
          matched_data.append(f"{row['編號']} {row['中字']}")
    
    # 回覆符合條件的資訊給使用者
    if matched_data:
        reply_message = "\n".join(matched_data)
    else:
        reply_message = "沒有符合條件的資料"
    

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

# 處理收到的文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    handle_message(event)
