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

    else:
        user_image_index = user_data.get('user_image_index', {})
        current_row_index = user_image_index[user_id]
        
        if user_image_index is None or not isinstance(user_image_index, dict):
            user_image_index = {}

    if user_input == str('抽'):
        random_row = random.choice(data)
        image_urls = random_row.get('圖片網址')  
        current_row_index = data.index(random_row)
        new_image_index = current_row_index
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
