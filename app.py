from flask import Flask
from bs4 import BeautifulSoup
import requests
import schedule
import time
import os
import setting
from dotenv import load_dotenv

app = Flask(__name__)

@app.route("/")

def hello():
    print('start')
    return "Start!"

LINETOKEN = os.getenv("LINE_TOKEN")


def checkTicket() :

    amz_headers = {
        'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Accept-Language': 'en-US, en;q=0.5'
    }
    
    url = "https://orders.ibon.com.tw/application/UTK02/utk0201_000.aspx?PERFORMANCE_ID=B04VR431&PRODUCT_ID=B04SGXOO"
    
    response = requests.get(
        url = url,
        headers=amz_headers
    ).text
    
    soup = BeautifulSoup(response, "html.parser")
    
    def get_available_tickets(soup, seat_ids):
        available_tickets = {}
        for seat_id in seat_ids:
            seat_value = soup.find(id=seat_id).text
            if seat_value == '已售完':
                available_tickets[seat_id] = seat_value
            else:
                available_tickets[seat_id] = int(seat_value)
        return available_tickets
    
    # 呼叫函數
    seat_ids = ["ctl00_ContentPlaceHolder1_AREA_LIST_ctl09_SEAT", "ctl00_ContentPlaceHolder1_AREA_LIST_ctl10_SEAT",
                "ctl00_ContentPlaceHolder1_AREA_LIST_ctl17_SEAT", "ctl00_ContentPlaceHolder1_AREA_LIST_ctl18_SEAT"]
    available_tickets = get_available_tickets(soup, seat_ids)
    
    # 使用範例：取得 front213 票數
    Availablefront213 = available_tickets["ctl00_ContentPlaceHolder1_AREA_LIST_ctl09_SEAT"]
    Availablefront214 = available_tickets["ctl00_ContentPlaceHolder1_AREA_LIST_ctl10_SEAT"]
    Availableend213 = available_tickets["ctl00_ContentPlaceHolder1_AREA_LIST_ctl17_SEAT"]
    Availableend214 = available_tickets["ctl00_ContentPlaceHolder1_AREA_LIST_ctl18_SEAT"]
    
    
    def check_available_and_notify(name, available_num):
        if available_num != '已售完':
            if available_num >= 2:
                msg = f" \n{name}票數 {available_num}"
                send_line_notify(msg)
        #else:
        #    print(f'{name}', available_num)
            
    def check_available_and_notify_213(name, available_num):
        if available_num != '已售完':
            if available_num >= 3:
                msg = f" \n{name}票數 {available_num}"
                send_line_notify(msg)
        #else:
        #    print(f'{name}', available_num)
            
    def send_line_notify(msg):
        #---------------Send Notification------------------
        url = "https://notify-api.line.me/api/notify"
        payload={'message':{msg}}
        headers = {'Authorization': 'Bearer ' + LINETOKEN}
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

    send_line_notify('start')       
    check_available_and_notify('front213', Availablefront213)
    check_available_and_notify('front214', Availablefront214)
    check_available_and_notify_213('end213', Availableend213)
    check_available_and_notify('end214', Availableend214)

# 呼叫函數
#checkTicket()

hello()

schedule.every(1).minutes.do(checkTicket)
while True:
    schedule.run_pending()
    time.sleep(1)
