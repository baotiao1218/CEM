# Estrus Manager LineNotify(EM_Notify) v1.1
# Dev 0.3 2022/11/12: Query條件修改
# Beta 0.4 2022/11/12: Query只篩選NextEstrus
# Prod 1.0, 2022/11/15: same as Beta 0.4 
# Prod 1.1, 2023/11/15: 修改date條件(now + localtime)

import requests, sqlite3, time, sys

token,LogPath = "",""
##
TestMode = 1 #1 or 0
# LINE Notify 權杖
token_prod = 'xxxxxxxxxxx'
token_test = 'xxxxxxxxxxx'
LogPath_prod = "logging_notify.log"
LogPath_test = "logging_notify_test.log"

if (TestMode == 0):
    token = token_prod
    LogPath = LogPath_prod
elif (TestMode == 1):
    token = token_test
    LogPath = LogPath_test

def Traceback(err):
    now = time.strftime('%H:%M:%S', time.localtime(time.time()))
    traceback = sys.exc_info()[2]
    with open("logging_notify.log", 'a') as logf:
        print (now, err, 'exception in line', traceback.tb_lineno, file = logf)

Query_Result = []
Query_Result.insert(0,[])

try:
    with open(LogPath, 'a') as logf:
        print (time.strftime('%H:%M:%S', time.localtime(time.time())) + " CEM Notifty Start!" , file = logf)
    
    messages_to_send = "\n母牛編號 | 上次發情日\n"

    db_connect = sqlite3.connect('CEM.db')
    cursorObj = db_connect.cursor()

    #DB_Query = cursorObj.execute('''SELECT * FROM Data_EstrusInfo WHERE NextEstrusDate = date('now') and NotifyStatus = 'N' order by Id''').fetchall()
    DB_Query = cursorObj.execute('''SELECT * FROM Data_EstrusInfo WHERE NextEstrusDate = date('now','localtime') order by Id''').fetchall()

    if (len(DB_Query) > 0):
        for SingleEstrusInfo in DB_Query:
            Query_Result[0].append("%s,%s,%s,%s" % (SingleEstrusInfo[0], SingleEstrusInfo[1], SingleEstrusInfo[2], SingleEstrusInfo[3]))
            messages_to_send = messages_to_send + " " + SingleEstrusInfo[1] + " | " + SingleEstrusInfo[2] + "\n"

            with open(LogPath, 'a') as logf:
                print((SingleEstrusInfo[0], SingleEstrusInfo[1], SingleEstrusInfo[2], SingleEstrusInfo[3]), file = logf)

            DbId = SingleEstrusInfo[0]
            cursorObj.execute('''UPDATE Data_EstrusInfo SET NotifyStatus = 'Y', LastNotifyTime = ? WHERE ID = ?''', (time.strftime('%Y-%m-%d %H:%M:%S'), DbId))
            db_connect.commit()
            with open(LogPath, 'a') as logf:
                print (DbId, file = logf)

        headers = { "Authorization": "Bearer " + token }
        data = { 'message': messages_to_send }

        requests.post("https://notify-api.line.me/api/notify",
        headers = headers, data = data)
    
    elif (len(DB_Query) == 0):
        with open(LogPath, 'a') as logf:
            #print(time.strftime('%H:%M:%S', time.localtime(time.time())) + " 沒有需通知的資料。 len(DB_Query) = " + len(DB_Query) , file = logf)
            print(time.strftime('%H:%M:%S', time.localtime(time.time()))," 沒有需通知的資料。 len(DB_Query) = " , len(DB_Query) , file = logf)


except Exception as e:
    Traceback(e)
