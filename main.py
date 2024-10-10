# Cattle Estrus Manager_API (CEM_API) v1.0
# Dev 0.1, 2022.09.26
# Dev 0.2, 2022.10.29
# Beta 0.3, 2022.11.06
# Beta 0.4, 2022.11.06: 增加Log
# Prod 1.0, 2022.11.15: same as Beta 0.4

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from Process import MSG_Process

import re, time

app = Flask(__name__)

#####
line_bot_api,handler,LogPath = "","",""
#####

TestMode = 0
line_bot_api_prod = LineBotApi('xxxxxxxxxxx')
handler_prod = WebhookHandler('xxxxxxxxxxx')
line_bot_api_test = LineBotApi('xxxxxxxxxxx')
handler_test = WebhookHandler('xxxxxxxxxxx')
LogPath_prod = "logging.log"
LogPath_test = "logging_test.log"

if (TestMode == 0):
    line_bot_api = line_bot_api_prod
    handler = handler_prod
    LogPath = LogPath_prod
elif (TestMode == 1):
    line_bot_api = line_bot_api_test
    handler = handler_test
    LogPath = LogPath_test

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #處理訊息(新增 刪除 查詢)
    #回傳確認(是->c, 否->cancel)/查詢內容
    #存入/刪除訊息(已儲存/刪除)
    try:
        with open(LogPath, 'a') as logf:
            logf.write(time.strftime('%H:%M:%S', time.localtime(time.time())) + " raw_message: " + event.message.text +"\n")
        
        return_msg = MSG_Process.Process_Raw_Message(event.message.text)
        messages_to_send = ""
        
        with open(LogPath, 'a') as logf:
            logf.write(time.strftime('%H:%M:%S', time.localtime(time.time())) + " processed_msg: " + str(return_msg)[0:-1] +"\n")
        
        if (return_msg[0] == "Insert"):
            if (return_msg[2] == "Success"):
                messages_to_send = "%s\n" % return_msg[3]
                for msg in return_msg[1]:
                    splitted_each_msg = msg.split(',')
                    messages_to_send = messages_to_send + splitted_each_msg[0] +" | "+ splitted_each_msg[1] +" | "+ splitted_each_msg[2] + "\n"
            elif (return_msg[2] == "Failed"):
                messages_to_send = return_msg[return_msg[3]]

        elif (return_msg[0] == "Delete"):
            if (return_msg[2] == "Success"):
                messages_to_send = "%s\n" % return_msg[3]
                for msg in return_msg[1]:
                    splitted_each_msg = msg.split(',')
                    messages_to_send = messages_to_send + splitted_each_msg[0] +" | "+ splitted_each_msg[1] +" | "+ splitted_each_msg[2] + "\n"
            elif (return_msg[2] == "Failed"):
                messages_to_send = return_msg[return_msg[3]]

        elif (return_msg[0] == "Undo"):
            if (return_msg[2] == "Success"):
                messages_to_send = "%s\n" % return_msg[3]
                for msg in return_msg[1]:
                    splitted_each_msg = msg.split(',')
                    messages_to_send = messages_to_send + splitted_each_msg[0] +" | "+ splitted_each_msg[1] +" | "+ splitted_each_msg[2] + "\n"
            elif (return_msg[2] == "Failed"):
                messages_to_send = return_msg[return_msg[3]]

        elif (return_msg[0] == "List"):
            if (return_msg[2] == "Success"):
                messages_to_send = "%s\n" % return_msg[3]
                for msg in return_msg[1]:
                    splitted_each_msg = msg.split(',')
                    messages_to_send = messages_to_send + splitted_each_msg[0] +" | "+ splitted_each_msg[1] +" | "+ splitted_each_msg[2] + " | " +splitted_each_msg[3] + "\n"
            elif (return_msg[2] == ""):
                messages_to_send = "查詢失敗！"

        elif (return_msg[0] == "Error"):
            print("test")

        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=messages_to_send))
        
        with open(LogPath, 'a') as logf:
            logf.write(time.strftime('%H:%M:%S', time.localtime(time.time())) + " final_message:" + messages_to_send +"\n")

    except Exception as e:
        MSG_Process.Traceback(e)

if __name__ == "__main__":
    #app.run()
    from waitress import serve
    if (TestMode == 0):
        serve(app, host="0.0.0.0", port=5000)
    if (TestMode == 1):
        serve(app, host="0.0.0.0", port=5001)