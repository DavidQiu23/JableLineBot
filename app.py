from flask import Flask, request, abort
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,TextMessageContent, 
)
from linebot.v3.messaging import(
    Configuration,ApiClient,MessagingApi,TextMessage, ReplyMessageRequest,CarouselColumn,URIAction,TemplateMessage,CarouselTemplate
)
from bs4 import BeautifulSoup
import os,re,requests,json


app = Flask(__name__)

geminiKey = os.getenv("GEMINI_KEY")
configuration = Configuration(access_token=os.getenv("LINE_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_SECRET"))
service = Service("/usr/bin/chromedriver")
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-extensions')
options.add_argument('--headless')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")

@app.route('/')
def index():
  return "hello world"

@app.route("/", methods=['POST'])
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
        print("Invalid signature. Please check your channel access token/channel secret.", flush=True)
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        text = event.message.text
        print("TextEven", flush=True)
        driver = webdriver.Chrome(service=service,options=options)
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            if(text == "義旻我要最新的車"):
                driver.get("https://jable.tv/latest-updates/")
                soup = BeautifulSoup(driver.page_source, "html.parser")
                dataList = soup.find_all('div', class_='video-img-box mb-e-20',limit=10)
                if(len(dataList) == 0):
                    line_bot_api.reply_message(ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="被J站當機機人擋起來了QQ")]
                    ))
                else:
                    carousel_template_message = TemplateMessage(
                    alt_text='最新列車啟動~',
                    template=CarouselTemplate(
                        columns=createColums(dataList)
                    ))
                    message = [TextMessage(text="兄弟 記得要節制"),carousel_template_message]
                    line_bot_api.reply_message(ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=message
                    ))
            elif(text == "義旻我要發燒列車"):
                driver.get('https://jable.tv/hot/')
                soup = BeautifulSoup(driver.page_source, "html.parser")
                dataList = soup.find_all('div', class_='video-img-box mb-e-20',limit=10)
                if(len(dataList) == 0):
                    line_bot_api.reply_message(ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="被J站當機機人擋起來了QQ")]
                    ))
                else:
                    carousel_template_message = TemplateMessage(
                    alt_text='發燒列車啟動~',
                    template=CarouselTemplate(
                        columns=createColums(dataList)
                    ))
                
                    message = [TextMessage(text="老鐵 來了 這是你要的"),carousel_template_message]
                    line_bot_api.reply_message(ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=message
                    ))
            elif(len(text.split(' ')) == 3):
                if(text.split(' ')[0] == "義旻我要"):
                    driver.get("https://jable.tv/search/"+text.split(' ')[1]+"/")
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    dataList = soup.find_all('div', class_='video-img-box mb-e-20',limit=10)
                    if(len(dataList) == 0):
                        line_bot_api.reply_message(ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="被J站當機機人擋起來了QQ")]
                        ))
                    else:
                        carousel_template_message = TemplateMessage(
                            alt_text=text.split(' ')[1]+'的片',
                            template=CarouselTemplate(
                                columns=createColums(dataList)
                            ))
                        message = [TextMessage(text=text.split(' ')[1]+"的片喔 我找找"),carousel_template_message]
                        line_bot_api.reply_message(ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=message
                        ))
            else:
                url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key='+geminiKey
                payload={
                    'contents': [{
                                    'role': "user",
                                    'parts': [{
                                        'text': text
                                    }]
                                }],
                    'tools': [
                        {
                            "google_search": {}
                        }
                    ]
                }
                res = requests.post(url,json=payload)
                resJson = json.loads(res.text)
                message = [TextMessage(text=resJson["candidates"][0]["content"]["parts"][0]["text"])]
                line_bot_api.reply_message(ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=message
                ))
        driver.quit()
    except Exception as e:
        print(e,flush=True)
    
def createColums(dataList):
    print("createColums", flush=True)
    columns = []
    for item in dataList:
        imgbox = item.find('div', class_='img-box cover-md')
        detail = item.find('div', class_='detail')
        text = re.match("([A-Za-z]+-\d+)(.+)",detail.select_one('a').getText()).group(2)
        if(len(text)>60):
            text = text[:56]+"...."
        columns.append(CarouselColumn(
                thumbnail_image_url=imgbox.select_one("img").get('data-src'),
                title=re.match("([A-Za-z]+-\d+)(.+)",detail.select_one('a').getText()).group(1),
                text=text,
                actions=[
                    URIAction(
                        label="熱血開尻",
                        uri=imgbox.select_one('a').get('href')+"?openExternalBrowser=1"
                    )
                ]
        ))
    return columns

if __name__ == "__main__":
    app.run()