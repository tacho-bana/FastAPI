from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from PIL import Image
import io
import torch
from torchvision import transforms, models

app = FastAPI()
#mpsを使うための設定
device = torch.device("mps")
#ResNet152を使用
#モデルの重みは、ImageNetで学習された重みを使用
model = models.resnet152(weights=models.ResNet152_Weights.DEFAULT)
model.to(device)
model.eval()
#画像の前処理を行う関数
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
#ラベルの読み込み
#imagenet_classes.txtには、ImageNetのクラス名が記載されている
with open("imagenet_classes.txt") as f:
    labels = [line.strip() for line in f.readlines()]
#ルートパスにアクセスしたときの処理
#HTMLResponseを指定することで、HTMLを返すことができる
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)
# /upload にアクセスしたときの処理
@app.post("/upload")
#画像ファイルを受け取り、推論結果を返す
async def upload_image(file: UploadFile = File(...)):
    #画像ファイルを読み込み、PILのImageオブジェクトに変換
    contents = await file.read()
    #画像をRGB形式に変換
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    #画像の前処理を行い、モデルに入力できる形式に変換
    input_tensor = preprocess(image)
    #モデルに入力するために次元を追加
    input_batch = input_tensor.unsqueeze(0).to(device)
    #モデルに画像を入力し、推論結果を取得
    with torch.no_grad():
        output = model(input_batch)

    #推論結果を確率に変換
    probablities = torch.nn.functional.softmax(output[0], dim=0)
    #確率が最も高いカテゴリを取得
    top1_prob, top1_catid = torch.max(probablities, 0)
    #カテゴリ名と確率を取得
    label = labels[top1_catid]
    #推論結果を文字列に変換
    prob = top1_prob.item()
    result = f"推論結果: {label}({prob*100:.2f}%)"
    return HTMLResponse(content=result, status_code=200)