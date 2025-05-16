import webview

def open_browser():
    webview.create_window('ARC Browser', 'https://lite.duckduckgo.com/lite/', width=480, height=320)
    webview.start()

if (__name__ == "__main__"):
    open_browser()