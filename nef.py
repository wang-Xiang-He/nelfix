from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from starlette.responses import RedirectResponse
import imaplib
import email
from email.header import decode_header
import requests
import schedule
import time
import threading

app = FastAPI()

def check_alive():
    try:
        response = requests.get("https://nelfix.onrender.com/alive")
        print("Alive endpoint response:", response.status_code)
    except Exception as e:
        print(f"Error calling alive endpoint: {e}")

def schedule_alive_check():
    schedule.every(10).minutes.do(check_alive)
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=schedule_alive_check, daemon=True).start()

@app.get("/")
async def redirect_to_link():
    # 帳戶信息
    username = "cming0236@gmail.com"
    password = "ziei mzdx wdnl rlbz"

    # 連接到IMAP服務器
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    # 登錄
    mail.login(username, password)

    # 選擇郵箱文件夾
    mail.select("inbox")

    # 搜尋特定條件的郵件
    search_criteria = 'X-GM-RAW "from:Netflix to:sqqw9442"'
    status, messages = mail.search(None, search_criteria)
    mail_ids = messages[0].split()

    if mail_ids:
        # 選擇最新的一封郵件
        latest_email_id = mail_ids[-1]

        # 獲取郵件數據
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                from_ = msg.get("From")
                to_ = msg.get("To")
                date_ = msg.get("Date")
                date_parsed = email.utils.parsedate_to_datetime(date_)

                print("Subject:", subject)
                print("From:", from_)
                print("To:", to_)
                print("Date:", date_parsed.strftime("%Y-%m-%d %H:%M:%S"))
            if subject == "重要資訊：如何更新 Netflix 同戶裝置":
                # 如果郵件內容是多部分的
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        # 跳過附件部分
                        if "attachment" in content_disposition:
                            continue
                        # 獲取郵件正文
                        if content_type == "text/plain" or content_type == "text/html":
                            try:
                                body = part.get_payload(decode=True).decode()
                            except Exception as e:
                                print(f"Error decoding part: {e}")
                                continue
                            if "是，這是我本人" in body:
                                index = body.find("是，這是我本人")
                                link = ''
                                while True:
                                    if body[index+10] != ']':
                                        link = link + body[index+10]
                                        index = index + 1
                                    else:
                                        print(link)
                                        break
                                print(len(link))
                                break
    else:
        print("No matching emails found.")
    # 關閉連接
    mail.logout()

    # 重定向到 link
    return RedirectResponse(url=link)


@app.get("/alive")
async def alive():
    print("alive")
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('nef:app', host="0.0.0.0", port=8880, reload=True)
