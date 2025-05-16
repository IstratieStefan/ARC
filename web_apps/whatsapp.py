import webview

def open_messages():
    webview.create_window('Whatsapp', 'https://web.whatsapp.com/', width=480, height=320)
    webview.start()

if (__name__ == "__main__"):
    open_messages()