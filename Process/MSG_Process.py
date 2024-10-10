#Estrus Manager Process Model (EM_PM) v1.0
# Beta 0.3:新增Log
# Beta 0.5: NotifyStatus
# Beta 0.7 
# Beta 0.8 
# Beta 0.9: CowId, Delete multi, List All
# Prod 1.0, 2022/11/15: same as Beta 0.9


import re, datetime, sqlite3, sys, time
from tkinter import E

TestMode = 0

LogPath = ""
if (TestMode == 0):
    Database = 'CEM.db'
    LogPath = "logging.log"
elif (TestMode == 1):
    Database = 'CEM_test.db'
    LogPath = "logging_test.log"
    
def Process_Raw_Message(RawMessage):

    #拆分多筆發情資訊
    SplittedRawMessage = RawMessage.split('\n')
    EstrusDataList = []

    try:
        
        if (bool(re.match(r'^[Uu][Nn][Dd][Oo]*',SplittedRawMessage[0]))):
            SingleEstrusInfo = SplittedRawMessage[0].split()
            
            with open(LogPath, 'a') as logf:
                logf.write(time.strftime('%H:%M:%S', time.localtime(time.time())) + " [Undo]Id:" + SingleEstrusInfo[1] +"\n")
            
            DB_EstrusDataList = Undo_Estrus_Info(SingleEstrusInfo[1])
            
            if (DB_EstrusDataList[2] == "Success"):
                DB_EstrusDataList.insert(3,"以下資料已成功恢復：\n資料編號 | 牛隻編號 | 發情時間\n")

            elif (DB_EstrusDataList[2] == "Failed"):
                DB_EstrusDataList.insert(3,"恢復失敗")

            return DB_EstrusDataList
        
        
        if (bool(re.match(r'^[Dd][Ee][Ll][Ee][Tt][Ee]*',SplittedRawMessage[0]))):
            DeleteNums = SplittedRawMessage[0].split()
            
            with open(LogPath, 'a') as logf:
                logf.write(str(DeleteNums[:len(DeleteNums)]) + "\n")

            DeleteList = []
            
            for Num in DeleteNums:
                if bool(re.match(r'[a-zA-Z]',Num)):
                    continue
                else:
                    DeleteList.append(Num)
                    
            with open(LogPath, 'a') as logf:
                logf.write(time.strftime('%H:%M:%S', time.localtime(time.time())) + " [Delete]Id:" + str(DeleteNums[1:len(DeleteNums)]) +"\n")
            
            DB_EstrusDataList = Delete_Estrus_Info(DeleteList)
            
            if (DB_EstrusDataList[2] == "Success"):
                DB_EstrusDataList.insert(3,"以下資料已成功刪除：\n資料編號 | 牛隻編號 | 發情時間\n")
                
            elif (DB_EstrusDataList[2] == "Failed"):
                DB_EstrusDataList.insert(3,"刪除失敗")

            return DB_EstrusDataList

        elif (bool(re.match(r'^[Ll][Ii][Ss][Tt]*',SplittedRawMessage[0]))):
            #EstrusDataList.append("List")
            DB_EstrusDataList = []
            try:
                SingleEstrusInfo = SplittedRawMessage[0].split()
                
                if (bool(re.match(r'^[Aa][Ll][Ll]',str(SingleEstrusInfo[1])))):
                    SingleEstrusInfo[1] = "9999"
                
                    with open(LogPath, 'a') as logf:
                        logf.write(time.strftime('%H:%M:%S', time.localtime(time.time())) + " [List]All" +"\n")
                
                elif (bool(re.match(r'^[0-9]+',str(SingleEstrusInfo[1])))):
                    DB_EstrusDataList.insert(3,"上次發情時間於%s天內的資料如下：\n資料編號 | 牛隻編號 | 發情時間 | 通知時間\n" % SingleEstrusInfo[1])
                    with open(LogPath, 'a') as logf:
                        logf.write(time.strftime('%H:%M:%S', time.localtime(time.time())) + " [List]Days:" + SingleEstrusInfo[1] +"\n")

                DB_EstrusDataList = List_Estrus_Info(SingleEstrusInfo[1])

                DB_EstrusDataList.insert(2,"Success")
                if (SingleEstrusInfo[1] == "9999"):
                    DB_EstrusDataList.insert(3,"所有資料如下：\n資料編號 | 牛隻編號 | 發情時間\n")
                else:
                    DB_EstrusDataList.insert(3,"上次發情時間於%s天內的資料如下：\n資料編號 | 牛隻編號 | 發情時間 | 通知時間\n" % SingleEstrusInfo[1])

            except:
                DB_EstrusDataList.insert(2,"Failed")
                DB_EstrusDataList.insert(3,"查詢失敗")

            with open(LogPath, 'a') as logf:
                logf.write(str(DB_EstrusDataList[0:-1]) + "\n")

            return DB_EstrusDataList

        elif (bool(re.match(r'^[0-9][0-9][a-zA-Z][0-9]+',SplittedRawMessage[0]))):
            EstrusDataList.append("Insert")
            EstrusDataList.append([])
            for RawMessageList in SplittedRawMessage:
                #將單筆發情資訊拆成編號與此次發情時間
                SingleEstrusInfo = RawMessageList.split()
                
                CowId = SingleEstrusInfo[0]
                EstrusDate = SingleEstrusInfo[1]
        
                #判斷EstrusDate是今天或是什麼日子
                if (EstrusDate.lower() == 'today'):
                    EstrusDate = str(datetime.date.today())
                
                elif ((len(EstrusDate) == 4) and (bool(re.match(r'\d{4}',EstrusDate)) == True)):
                    EstrusDate = str(datetime.date.today().year)+EstrusDate
                    EstrusDate = datetime.datetime.strptime(EstrusDate, '%Y%m%d')

                elif ((len(EstrusDate) == 8) and (bool(re.match(r'\d{8}',EstrusDate)) == True)):
                    EstrusDate = datetime.datetime.strptime(EstrusDate, '%Y%m%d')

                else:
                    EstrusDataList.append("Failed")
                    EstrusDataList.append("時間格式有誤")
                    return EstrusDataList
                
                #下次發情期為本次+28天
                NextEstrusDate = EstrusDate + datetime.timedelta(days = 21)
                EstrusDataList[1].append('%s,%s,%s' %(str(CowId),str(EstrusDate.date()),str(NextEstrusDate.date())))
                '''with open(LogPath, 'a') as logf:
                    print(type(EstrusDate), type(NextEstrusDate), file = logf)
                    print("EstrusDate:",EstrusDate,"NextEstrusDate:", NextEstrusDate, file = logf)
                    print("EstrusDataList:",EstrusDataList, file = logf)
                '''
            #插入DB-Insert
            DB_Return = Insert_Estrus_Info(EstrusDataList[1])

            if (DB_Return == "Success"):
                EstrusDataList.append("Success")
                EstrusDataList.append("以下資料已儲存成功：\n牛隻編號 | 發情時間 | 通知時間\n")

            elif (DB_Return == "Failed"):
                EstrusDataList.append("Failed")
                EstrusDataList.append("資料儲存發生錯誤")

        else:
            EstrusDataList.append("Failed")
            EstrusDataList.append("輸入內容或格式有誤")

    except Exception as e:
        Traceback(e)
        EstrusDataList.append("Failed")
        EstrusDataList.append("輸入內容或格式有誤")

    return EstrusDataList


def Insert_Estrus_Info(EstrusDataList):
    db_connect = sqlite3.connect(Database)
    cursorObj = db_connect.cursor()

    try:
        for EstrusInfo in EstrusDataList:
            EstrusInfo = EstrusInfo.split(',')

        #檢查最後Id 
            selectDB = cursorObj.execute('''select MAX(id) from Data_EstrusInfo''')
            LastId = selectDB.fetchone()
            
            #Insert資料
            with open(LogPath, 'a') as logf:
                logf.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " [Add]Id:" + str(LastId[0] + 1) + ", CowId:" + EstrusInfo[0] + ", EstrusDate:" + EstrusInfo[1] + ", NextEstrusDate:" + EstrusInfo[2] + ", Y" + ", LINE" +"\n")

            data_tuple = ((LastId[0] + 1), EstrusInfo[0], EstrusInfo[1], EstrusInfo[2], "Y", "LINE", "N", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), "null")
        
            insert_sql = '''INSERT INTO DATA_EstrusInfo (Id,CowId,EstrusDate,NextEstrusDate,Status,Platform,NotifyStatus,CreatedTime,LastNotifyTime) VALUES (?,?,?,?,?,?,?,?,?)''' 
            cursorObj.execute(insert_sql, data_tuple)
            db_connect.commit()

        return "Success"
    
    except Exception as e:
        Traceback(e)
        with open(LogPath, 'a') as logf:
            print ("儲存失敗:", e, file = logf)
        return "Failed"


def List_Estrus_Info(Days):
    db_connect = sqlite3.connect(Database)
    cursorObj = db_connect.cursor()
    DB_EstrusDataList = []

    with open(LogPath, 'a') as logf:
        print ("Days:",[(Days)], file = logf)
    try:
        DB_EstrusDataList.insert(0, 'List')
        EstrusInfoFromDB = cursorObj.execute('''SELECT * FROM Data_EstrusInfo WHERE EstrusDate <= date('now') and EstrusDate >= date('now','-%s day') and Status = 'Y' order by EstrusDate;'''% Days).fetchall()
        DB_EstrusDataList.insert(1, [])
        for SingleEstrusInfo in EstrusInfoFromDB:
            DB_EstrusDataList[1].append("%s,%s,%s,%s" % (SingleEstrusInfo[0], SingleEstrusInfo[1], SingleEstrusInfo[2], SingleEstrusInfo[3]))
        
        with open(LogPath, 'a') as logf:
            print ("DB_EstrusDataList:",DB_EstrusDataList, file = logf)
        DB_EstrusDataList.insert(2, 'Success')
    except Exception as e:
        Traceback(e)
        with open(LogPath, 'a') as logf:
            print ("查詢失敗:", e, file = logf)
    
    return DB_EstrusDataList


def List_Estrus_Info_CowId(CowId):
    db_connect = sqlite3.connect('CEM.db')
    cursorObj = db_connect.cursor()
    DB_EstrusDataList = []

    with open(LogPath, 'a') as logf:
        print ("CowId:",[(CowId)], file = logf)
    try:
        DB_EstrusDataList.insert(0, 'List')
        EstrusInfoFromDB = cursorObj.execute('''SELECT * FROM Data_EstrusInfo WHERE CowId = %s and Status = 'Y' order by EstrusDate;'''% CowId).fetchall()
        DB_EstrusDataList.insert(1, [])
        for SingleEstrusInfo in EstrusInfoFromDB:
            DB_EstrusDataList[1].append("%s,%s,%s,%s" % (SingleEstrusInfo[0], SingleEstrusInfo[1], SingleEstrusInfo[2], SingleEstrusInfo[3]))
        
        with open(LogPath, 'a') as logf:
            print ("DB_EstrusDataList:",DB_EstrusDataList, file = logf)
        DB_EstrusDataList.insert(2, 'Success')

    except Exception as e:
        Traceback(e)
        with open(LogPath, 'a') as logf:
            print ("查詢失敗:", e, file = logf)


def Delete_Estrus_Info(DBId):
    db_connect = sqlite3.connect(Database)
    cursorObj = db_connect.cursor()

    DB_EstrusDataList = []
    DB_EstrusDataList.insert(0, 'Delete')
    DB_EstrusDataList.insert(1, [])
    try:
        for Id in DBId:
            cursorObj.execute('''UPDATE Data_EstrusInfo SET Status = 'D' WHERE ID = ?''', (Id,))
            db_connect.commit()
            Delete_Result = cursorObj.execute('''SELECT * FROM Data_EstrusInfo WHERE Id = ?''', (Id,)).fetchall()

            if (Delete_Result[0][0] == int(Id) and Delete_Result[0][4] == "D"):
                DB_EstrusDataList[1].append("%s,%s,%s"% (Delete_Result[0][0],Delete_Result[0][1],Delete_Result[0][2]))

            else:
                DB_EstrusDataList.insert(2,"Failed")

        DB_EstrusDataList.insert(2,"Success")
        with open(LogPath, 'a') as logf:
            print (DB_EstrusDataList, file = logf)

    except Exception as e:
        Traceback(e)
        with open(LogPath, 'a') as logf:
            print ("刪除失敗:", e, file = logf)
        #DB_EstrusDataList.insert(2,"Failed")
        #return DB_EstrusDataList

    return DB_EstrusDataList


def Undo_Estrus_Info(DBId):
    db_connect = sqlite3.connect(Database)
    cursorObj = db_connect.cursor()

    DB_EstrusDataList = []
    DB_EstrusDataList.insert(0, 'Undo')
    DB_EstrusDataList.insert(1, [])
    try:
        cursorObj.execute('''UPDATE Data_EstrusInfo SET Status = 'Y' WHERE ID = ?''', (DBId,))
        db_connect.commit()
        Undo_Result = cursorObj.execute('''SELECT * FROM Data_EstrusInfo WHERE Id = ?''', (DBId,)).fetchall()

        if (Undo_Result[0][0] == int(DBId) and Undo_Result[0][4] == "Y"):
            DB_EstrusDataList[1].append("%s,%s,%s"% (Undo_Result[0][0],Undo_Result[0][1],Undo_Result[0][2]))
            DB_EstrusDataList.insert(2,"Success")
            with open(LogPath, 'a') as logf:
                print (DB_EstrusDataList, file = logf)

        else:
            DB_EstrusDataList.insert(2,"Failed")
        
    except Exception as e:
        Traceback(e)
        with open(LogPath, 'a') as logf:
            print ("恢復失敗:", e, file = logf)
        return "Failed"

    return DB_EstrusDataList

def Traceback(err):
    now = time.strftime('%H:%M:%S', time.localtime(time.time()))
    traceback = sys.exc_info()[2]
    with open(LogPath, 'a') as logf:
        print (now, err, 'exception in line', traceback.tb_lineno, file = logf)