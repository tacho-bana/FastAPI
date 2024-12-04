from fastapi import FastAPI
#FastAPIのインスタンスを作成
#インスタンスとは、クラスを実体化したもの
app = FastAPI()

#ルートパスにアクセスした時の処理
@app.get("/")
#非同期処理を行うためにasyncをつける
#非同期処理とは、処理を逐次実行せず、並行して処理を行うこと
async def read_root():
    return {"message": "Hello Tacho"}