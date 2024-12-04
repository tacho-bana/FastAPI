# Form データを受け取り、HTML ファイルを返す
from fastapi import FastAPI, Form
# HTMLResponseとは、FastAPIでHTMLを返すためのクラスです。
from fastapi.responses import HTMLResponse

app = FastAPI()

# ルートパスにアクセスしたときに、index.htmlを返す
# response_class=HTMLResponse を指定することで、HTMLを返すことができる
@app.get("/", response_class=HTMLResponse)
async def read_index():
    # index.html を読み込み、その内容を返す
    with open("index.html", encoding="utf-8") as f:
        return f.read()

# /calculate にアクセスしたときに、formデータを受け取り、result.htmlを返す
@app.post("/calculate")
#formデータを受け取る
async def calculate(x: float = Form(...), y: float = Form(...)):
    result = x + y
    # result.html を読み込み、プレースホルダーを置き換え
    with open("result.html", encoding="utf-8") as f:
        html_content = f.read()
    #str()関数は、引数を文字列に変換する関数
    #replace()関数は、文字列の一部を置換する関数
    #{x}という文字列をxの値に置き換える
    html_content = html_content.replace("{x}", str(x))
    html_content = html_content.replace("{y}", str(y))
    html_content = html_content.replace("{result}", str(result))
    return HTMLResponse(content=html_content)