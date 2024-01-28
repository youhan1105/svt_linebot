from linebot.models import PostbackEvent, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction, URIAction, CarouselTemplate, CarouselColumn

def handle_menu(event, line_bot_api):
    if isinstance(event, PostbackEvent):
        if event.postback.data == 'menu_1':
            # 發送多頁訊息
            carousel_template_message = create_carousel_template()
            line_bot_api.reply_message(event.reply_token, carousel_template_message)
        elif event.postback.data == 'menu_2':
            # 發送 LIFF 網頁
            liff_url = 'YOUR_LIFF_URL'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=liff_url))
        elif event.postback.data == 'menu_3':
            # 發送另一個 LIFF 網頁
            another_liff_url = 'ANOTHER_LIFF_URL'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=another_liff_url))

def create_carousel_template():
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(
            thumbnail_image_url='IMAGE_URL_1',
            title='Page 1',
            text='Page 1 description',
            actions=[
                MessageAction(label='Button 1', text='Button 1 clicked')
            ]
        ),
        CarouselColumn(
            thumbnail_image_url='IMAGE_URL_2',
            title='Page 2',
            text='Page 2 description',
            actions=[
                MessageAction(label='Button 2', text='Button 2 clicked')
            ]
        ),
        CarouselColumn(
            thumbnail_image_url='IMAGE_URL_3',
            title='Page 3',
            text='Page 3 description',
            actions=[
                MessageAction(label='Button 3', text='Button 3 clicked')
            ]
        ),
        CarouselColumn(
            thumbnail_image_url='IMAGE_URL_4',
            title='Page 4',
            text='Page 4 description',
            actions=[
                MessageAction(label='Button 4', text='Button 4 clicked')
            ]
        ),
        CarouselColumn(
            thumbnail_image_url='IMAGE_URL_5',
            title='Page 5',
            text='Page 5 description',
            actions=[
                MessageAction(label='Button 5', text='Button 5 clicked')
            ]
        )
    ])
    return TemplateSendMessage(alt_text='Carousel template', template=carousel_template)
