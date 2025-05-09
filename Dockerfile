FROM python:3.9-slim

WORKDIR /app

# 必要なライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# Cloud Run環境変数PORTを取得して使用
CMD streamlit run --server.port=$PORT --server.address=0.0.0.0 app.py
