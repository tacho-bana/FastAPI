from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
import io
import torch
from torchvision import transforms, models

app = FastAPI()

# 静的ファイルとテンプレート設定
app.mount("/static", StaticFiles(directory="static"), name="static")
#これは、テンプレートファイルを読み込むための設定です。
templates = Jinja2Templates(directory="static")

# mpsを使うための設定
device = torch.device("mps")

# ResNet152モデルのロード
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

# 日本語クラス名の読み込み
with open("imagenet_classes_jp.txt", encoding="utf-8") as f:
    labels = [line.strip() for line in f.readlines()]

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # 画像を保存しておく
    image_path = f"static/uploaded_image.jpg"
    image.save(image_path)

    # 前処理と推論
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_batch)

    # Top5分類結果を取得
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    top5_prob, top5_catid = torch.topk(probabilities, 5)
    results = [(labels[catid], prob.item()) for prob, catid in zip(top5_prob, top5_catid)]

    # テンプレートに渡す
    return templates.TemplateResponse("result.html", {
        "request": {},  # 必須パラメータ
        "results": results,
        "image_url": f"/static/uploaded_image.jpg"
    })
