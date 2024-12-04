from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
import io
import torch
from torchvision import transforms, models
import base64
import os

app = FastAPI()

# テンプレートディレクトリの設定
templates = Jinja2Templates(directory="templates")

# デバイスの自動選択
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

# ResNet152モデルの読み込み
model = models.resnet152(weights=models.ResNet152_Weights.DEFAULT)
model.to(device)
model.eval()

# 画像の前処理
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# 日本語ラベルの読み込み
labels_path = "imagenet_classes_jp.txt"
if not os.path.exists(labels_path):
    raise FileNotFoundError(f"ラベルファイルが見つかりません: {labels_path}")

with open(labels_path, encoding='utf-8') as f:
    labels = [line.strip() for line in f.readlines()]

# ルートパスにアクセスしたときの処理
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# /upload にアクセスしたときの処理
@app.post("/upload", response_class=HTMLResponse)
async def upload_image(request: Request, file: UploadFile = File(...)):
    try:
        # 画像ファイルを読み込み、PILのImageオブジェクトに変換
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 画像の前処理
        input_tensor = preprocess(image)
        input_batch = input_tensor.unsqueeze(0).to(device)
        
        # モデルによる推論
        with torch.no_grad():
            output = model(input_batch)
        
        # Top5の予測結果を取得
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top5_prob, top5_catid = torch.topk(probabilities, 5)
        
        top5 = []
        for i in range(top5_prob.size(0)):
            top5.append({"label": labels[top5_catid[i]], "prob": top5_prob[i].item() * 100})

        # 画像をBase64エンコード
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        img_data = f"data:image/jpeg;base64,{img_str}"
        
        # 結果をテンプレートに渡す
        return templates.TemplateResponse("result.html", {
            "request": request,
            "image": img_data,
            "predictions": top5
        })
    
    except Exception as e:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "error": f"エラーが発生しました: {e}"
        })