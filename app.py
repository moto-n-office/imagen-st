import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import json

# ページ設定
st.set_page_config(
    page_title="Gemini画像生成",
    page_icon="🎨",
    layout="wide",
)

# タイトルとヘッダー
st.title("Gemini AI 画像生成アプリ")
st.markdown("Gemini 2.0を使って、テキストプロンプトから画像を生成できます。")

# サイドバーにAPI設定
with st.sidebar:
    st.header("API設定")
    api_url = st.text_input(
        "API URL", 
        value="https://gemini-api-xxxxxx-uc.a.run.app/generate-image",
        help="画像生成APIのエンドポイントURL"
    )
    
    st.markdown("---")
    st.header("About")
    st.markdown("このアプリはGemini 2.0 Flash Preview Image Generationを使用しています。")

# メインコンテンツ
col1, col2 = st.columns([1, 1])

with col1:
    st.header("プロンプト入力")
    
    # プロンプト入力
    prompt = st.text_area(
        "画像生成プロンプト",
        value="富士山と桜の風景、春の朝",
        height=150,
        help="生成したい画像の説明を入力してください"
    )
    
    # 生成ボタン
    if st.button("画像を生成", type="primary", use_container_width=True):
        with st.spinner("画像を生成中..."):
            try:
                # APIリクエスト
                response = requests.post(
                    api_url,
                    json={"prompt": prompt},
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                
                # レスポンス確認
                if response.status_code == 200:
                    result = response.json()
                    if "image" in result:
                        # 画像データを保存
                        st.session_state.generated_image = result["image"]
                        st.session_state.last_prompt = prompt
                        st.success("画像が生成されました！")
                    else:
                        st.error("画像データがレスポンスに含まれていません")
                else:
                    error_message = f"エラー: {response.status_code}"
                    try:
                        error_detail = response.json().get("error", "詳細不明")
                        error_message += f" - {error_detail}"
                    except:
                        pass
                    st.error(error_message)
            except Exception as e:
                st.error(f"リクエスト中にエラーが発生しました: {str(e)}")
    
    # 履歴表示
    if "generated_image" in st.session_state:
        st.markdown("---")
        st.subheader("生成プロンプト")
        st.write(st.session_state.last_prompt)

# 生成画像表示エリア
with col2:
    st.header("生成画像")
    if "generated_image" in st.session_state:
        # Base64デコードして画像を表示
        image_data = base64.b64decode(st.session_state.generated_image)
        img = Image.open(BytesIO(image_data))
        st.image(img, use_column_width=True)
        
        # ダウンロードボタン
        buf = BytesIO()
        img.save(buf, format="PNG")
        btn = st.download_button(
            label="画像をダウンロード",
            data=buf.getvalue(),
            file_name="gemini_generated_image.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.info("プロンプトを入力して「画像を生成」ボタンをクリックしてください")

# フッター
st.markdown("---")
st.markdown("Powered by Google Vertex AI Gemini 2.0")
