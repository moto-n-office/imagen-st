import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import json
import time
import os

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
    
    # 詳細設定
    st.markdown("---")
    st.header("詳細設定")
    aspect_ratio = st.selectbox(
        "アスペクト比",
        options=["16:9", "1:1", "3:4", "4:3", "9:16"],
        index=0,
        help="生成する画像のアスペクト比"
    )
    
    seed = st.number_input(
        "シード値",
        min_value=0,
        max_value=1000000,
        value=0,
        help="同じ結果を再現するためのシード値（0はランダム）"
    )
    
    # デバッグモード
    st.markdown("---")
    debug_mode = st.checkbox("デバッグモード", value=True, help="APIレスポンスの詳細を表示します")
    
    st.markdown("---")
    st.header("About")
    st.markdown("このアプリはVertex AI Gemini 2.0を使用した画像生成APIと連携しています。")

# メインコンテンツ - 2カラムレイアウト
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
    
    # ネガティブプロンプト
    negative_prompt = st.text_area(
        "ネガティブプロンプト（任意）",
        value="",
        height=100,
        help="画像に含めたくない要素を指定します"
    )
    
    # 生成ボタン
    if st.button("画像を生成", type="primary", use_container_width=True):
        with st.spinner("画像を生成中..."):
            try:
                # リクエスト開始時間
                start_time = time.time()
                
                # APIリクエストデータ
                request_data = {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt
                }
                
                # シード値が指定されている場合
                if seed > 0:
                    request_data["seed"] = seed
                
                # アスペクト比を追加
                if aspect_ratio:
                    request_data["aspect_ratio"] = aspect_ratio
                
                # デバッグ表示
                if debug_mode:
                    st.subheader("リクエスト内容")
                    st.json(request_data)
                
                # APIリクエスト
                response = requests.post(
                    api_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=120  # タイムアウトを長めに設定
                )
                
                # 処理時間
                process_time = time.time() - start_time
                
                # デバッグ情報
                if debug_mode:
                    st.subheader("APIレスポンス詳細")
                    debug_container = st.container()
                    with debug_container:
                        col_status, col_time = st.columns(2)
                        with col_status:
                            st.metric("ステータスコード", response.status_code)
                        with col_time:
                            st.metric("処理時間", f"{process_time:.2f}秒")
                        
                        st.markdown("#### レスポンスヘッダー")
                        st.json(dict(response.headers))
                        
                        st.markdown("#### レスポンス内容")
                        try:
                            resp_json = response.json()
                            # データ量が多い場合は画像データを省略して表示
                            if "data" in resp_json and "images" in resp_json["data"] and resp_json["data"]["images"]:
                                display_json = resp_json.copy()
                                images = display_json["data"]["images"]
                                # 各画像を省略表示に置き換え
                                display_json["data"]["images"] = [
                                    f"[BASE64エンコード画像データ: {len(img)}文字]" for img in images
                                ]
                                st.json(display_json)
                            else:
                                st.json(resp_json)
                            
                            # レスポンス構造の確認
                            st.text(f"レスポンスのキー: {list(resp_json.keys())}")
                            if "data" in resp_json:
                                st.text(f"data内のキー: {list(resp_json['data'].keys())}")
                                if "images" in resp_json["data"]:
                                    st.text(f"images配列の長さ: {len(resp_json['data']['images'])}")
                        except:
                            st.text("JSONではないレスポンス:")
                            st.text(response.text[:1000])  # 長すぎる場合は一部のみ表示
                
                # レスポンス確認
                if response.status_code == 200:
                    result = response.json()
                    
                    # 正しいパスから画像データを取得
                    if ("status" in result and result["status"] == "success" and 
                            "data" in result and "images" in result["data"] and 
                            result["data"]["images"]):
                        # 画像データを保存
                        st.session_state.generated_image = result["data"]["images"][0]
                        st.session_state.last_prompt = prompt
                        st.session_state.last_negative_prompt = negative_prompt
                        st.session_state.last_aspect_ratio = aspect_ratio
                        st.session_state.last_seed = seed if seed > 0 else None
                        st.success("画像が生成されました！")
                    else:
                        # 構造を表示して問題をデバッグ
                        st.error("画像データが正しい形式で返されていません")
                        st.write("レスポンス構造:", result.keys())
                        if "data" in result:
                            st.write("data内の構造:", result["data"].keys())
                            if "images" in result["data"]:
                                st.write("images配列の長さ:", len(result["data"]["images"]))
                else:
                    error_message = f"エラー: {response.status_code}"
                    try:
                        error_detail = response.json().get("error", "詳細不明")
                        error_message += f" - {error_detail}"
                    except:
                        error_message += f" - レスポンス: {response.text[:200]}..."
                    st.error(error_message)
            except Exception as e:
                st.error(f"リクエスト中にエラーが発生しました: {str(e)}")
    
    # 履歴表示
    if "generated_image" in st.session_state:
        st.markdown("---")
        st.subheader("生成設定")
        
        # 設定情報を表示
        settings_container = st.container()
        with settings_container:
            st.markdown(f"**プロンプト**: {st.session_state.last_prompt}")
            
            if st.session_state.last_negative_prompt:
                st.markdown(f"**ネガティブプロンプト**: {st.session_state.last_negative_prompt}")
            
            col_aspect, col_seed = st.columns(2)
            with col_aspect:
                st.markdown(f"**アスペクト比**: {st.session_state.last_aspect_ratio}")
            with col_seed:
                seed_value = st.session_state.last_seed if hasattr(st.session_state, 'last_seed') else "ランダム"
                st.markdown(f"**シード値**: {seed_value}")

# 生成画像表示エリア
with col2:
    st.header("生成画像")
    if "generated_image" in st.session_state:
        try:
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
                file_name="generated_image.png",
                mime="image/png",
                use_container_width=True
            )
        except Exception as img_error:
            st.error(f"画像の表示中にエラーが発生しました: {str(img_error)}")
            
            # デバッグ情報
            if debug_mode:
                st.text(f"画像データの先頭部分: {st.session_state.generated_image[:50]}...")
                st.text(f"画像データの長さ: {len(st.session_state.generated_image)}")
    else:
        st.info("プロンプトを入力して「画像を生成」ボタンをクリックしてください")

# フッター
st.markdown("---")
st.markdown("Powered by Google Vertex AI Gemini 2.0")

# Cloud Run対応のポート設定
if __name__ == "__main__":
    # 環境変数PORTの値を取得（デフォルトは8501）
    port = int(os.environ.get("PORT", 8501))
    # デバッグ情報としてポート設定を表示
    print(f"Configured to listen on port {port}")
    
    # StreamlitをCloud Run互換モードで起動
    import sys
    import subprocess
    cmd = [
        "streamlit", 
        "run", 
        sys.argv[0],
        "--server.port", str(port),
        "--server.address", "0.0.0.0"
    ]
    subprocess.call(cmd)
