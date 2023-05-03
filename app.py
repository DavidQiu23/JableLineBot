from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,CarouselColumn,URIAction,TemplateSendMessage,CarouselTemplate
)
from webdriver_manager.chrome import ChromeDriverManager
import os,re,requests,undetected_chromedriver
from bs4 import BeautifulSoup

ChromeDriverManager().install()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("TOKEN"))
handler = WebhookHandler(os.getenv("SECRET"))

history = []

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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("TextEven")
    global history
    global driverPath
    options = undetected_chromedriver.ChromeOptions()
    options.add_argument( '--no-sandbox' )
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-popup-blocking')
    driver = undetected_chromedriver.Chrome(options=options,headless=True, version_main=112) 
    if(event.message.text == "義旻我要最新的車"):
        # response = scraper.get("https://jable.tv/latest-updates/")
        soup = BeautifulSoup(response.text, "html.parser")
        dataList = soup.find_all('div', attrs={'class':'video-img-box mb-e-20'},limit=10)
    
        carousel_template_message = TemplateSendMessage(
        alt_text='最新列車啟動~',
        template=CarouselTemplate(
            columns=createColums(dataList)
        ))
        message = [TextSendMessage(text="兄弟 記得要節制"),carousel_template_message]
        line_bot_api.reply_message(event.reply_token,message)
    elif(event.message.text == "義旻我要發燒列車"):
        response = driver.get('https://jable.tv')
        # response = scraper.get('https://jable.tv').page_source
        # soup = BeautifulSoup(response.text, "html.parser")
        soup = BeautifulSoup(response.page_source, "html.parser")
        dataList = soup.find_all('div', attrs={'class':'video-img-box mb-e-20'},limit=10)
        
        carousel_template_message = TemplateSendMessage(
        alt_text='發燒列車啟動~',
        template=CarouselTemplate(
            columns=createColums(dataList)
        ))
    
        message = [TextSendMessage(text="老鐵 來了 這是你要的"),carousel_template_message]
        line_bot_api.reply_message(event.reply_token,message)
    elif(len(event.message.text.split(' ')) == 3):
        if(event.message.text.split(' ')[0] == "義旻我要"):
            # response = scraper.get("https://jable.tv/search/"+event.message.text.split(' ')[1]+"/")
            soup = BeautifulSoup(response.text, "html.parser")
            dataList = soup.find_all('div', attrs={'class':'video-img-box mb-e-20'},limit=10)

            carousel_template_message = TemplateSendMessage(
                alt_text=event.message.text.split(' ')[1]+'的片',
                template=CarouselTemplate(
                    columns=createColums(dataList)
                ))
            message = [TextSendMessage(text=event.message.text.split(' ')[1]+"的片喔 我找找"),carousel_template_message]
            line_bot_api.reply_message(event.reply_token,message)
    elif(event.message.text == "清除記憶"):
        history = []
        message = [TextSendMessage(text="記憶已清除")]
        line_bot_api.reply_message(event.reply_token,message)
    else:
        history.append({"role": "user", "content": event.message.text})
        result = requests.post("https://api.openai.com/v1/chat/completions",json={"model": "gpt-3.5-turbo","messages": history},headers={"Authorization":"Bearer "+os.getenv("GPT")})
        result = result.json()
        history.append(result["choices"][0]["message"])
        message = [TextSendMessage(text=result["choices"][0]["message"]["content"])]
        line_bot_api.reply_message(event.reply_token,message)
    

def createColums(dataList):
    print("createColums")
    columns = []
    for item in dataList:
        imgbox = item.find('div', attrs={'class':'img-box cover-md'})
        detail = item.find('div', attrs={'class':'detail'})
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