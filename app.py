from flask import Flask, request, abort

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

from webdriver_manager.chrome import ChromeDriverManager
import os,re,requests,undetected_chromedriver
from bs4 import BeautifulSoup

driverPath = ChromeDriverManager(path="./chromedriver").install()
options = undetected_chromedriver.ChromeOptions()
options.add_argument( '--headless' )
options.add_argument( '--no-sandbox' )
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")
options.add_argument('--disable-popup-blocking')
driver = undetected_chromedriver.Chrome(options=options,headless=True, version_main=113,driver_executable_path=driverPath) 

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv("TOKEN"))
#line_bot_api = LineBotApi(os.getenv("TOKEN"))
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
        print("Invalid signature. Please check your channel access token/channel secret.", flush=True)
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event, flush=True):
    try:
        text = event.message.text
        print("TextEven", flush=True)
        global history
        global driver
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            if(text == "義旻我要最新的車"):
                driver.get("https://jable.tv/latest-updates/")
                soup = BeautifulSoup(driver.page_source, "html.parser")
                dataList = soup.find_all('div', attrs={'class':'video-img-box mb-e-20'},limit=10)
            
                carousel_template_message = TemplateMessage(
                alt_text='最新列車啟動~',
                template=CarouselTemplate(
                    columns=createColums(dataList)
                ))
                message = [TextMessage(text="兄弟 記得要節制"),carousel_template_message]
                line_bot_api.reply_message(event.reply_token,message)
            elif(text == "義旻我要發燒列車"):
                driver.get('https://jable.tv/hot/')
                soup = BeautifulSoup(driver.page_source, "html.parser")
                dataList = soup.find_all('div', attrs={'class':'video-img-box mb-e-20'},limit=10)
                
                carousel_template_message = TemplateMessage(
                alt_text='發燒列車啟動~',
                template=CarouselTemplate(
                    columns=createColums(dataList)
                ))
            
                message = [TextMessage(text="老鐵 來了 這是你要的"),carousel_template_message]
                line_bot_api.reply_message(event.reply_token,message)
            elif(len(text.split(' ')) == 3):
                if(text.split(' ')[0] == "義旻我要"):
                    driver.get("https://jable.tv/search/"+text.split(' ')[1]+"/")
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    dataList = soup.find_all('div', attrs={'class':'video-img-box mb-e-20'},limit=10)

                    carousel_template_message = TemplateMessage(
                        alt_text=text.split(' ')[1]+'的片',
                        template=CarouselTemplate(
                            columns=createColums(dataList)
                        ))
                    message = [TextMessage(text=text.split(' ')[1]+"的片喔 我找找"),carousel_template_message]
                    line_bot_api.reply_message(event.reply_token,message)
            elif(text == "清除記憶"):
                history = []
                message = [TextMessage(text="記憶已清除")]
                line_bot_api.reply_message(event.reply_token,message)
            else:
                history.append({"role": "user", "content": text})
                result = requests.post("https://api.openai.com/v1/chat/completions",json={"model": "gpt-3.5-turbo","messages": history},headers={"Authorization":"Bearer "+os.getenv("GPT")})
                result = result.json()
                print(result,flush=True)
                history.append(result["choices"][0]["message"])
                message = [TextMessage(text=result["choices"][0]["message"]["content"])]
                line_bot_api.reply_message(event.reply_token,message)
    except Exception as e:
        print(e,flush=True)
    

def createColums(dataList):
    print("createColums", flush=True)
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