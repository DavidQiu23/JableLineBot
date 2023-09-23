## 指令 (無法跳過jable機器人偵測)

- 義旻我要發燒列車
- 義旻我要最新的車
- 義旻我要 {名子} 的車
- ~~除此之外以chatGPT回覆~~ chatGPT API 免費試用期已過

## 筆記

- 目前架設在Render雲端平台，使用Docker服務
- Docker建置python環境並且下載安裝chrome
- 使用`webdriver_manager`套件下載chrome驅動，給`undetected_chromedriver`使用，`undetected_chromedriver`的設定版本要112以上並且開啟無頭模式
