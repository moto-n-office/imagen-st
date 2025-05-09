import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import json
import time

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
        value="/generate",
        help="画像生成APIのエンドポイントURL"
    )
    
    st.markdown("---")
    st.header("About")
    st.markdown("このアプリはGemini 2.0 Flash Preview Image Generationを使用しています。")
    
    # デバッグモード
    debug_mode = st.checkbox("デバッグモード", value=True, help="APIレスポンスの詳細を表示します")

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
                # リクエスト開始時間
                start_time = time.time()
                
                # APIリクエスト
                response = requests.post(
                    api_url,
                    json={"prompt": prompt},
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
                            # データ量が多い場合はキーのみ表示
                            if "image" in resp_json and len(resp_json["image"]) > 1000:
                                display_json = resp_json.copy()
                                display_json["image"] = f"[BASE64エンコード画像データ: {len(resp_json['image'])}文字]"
                                st.json(display_json)
                            else:
                                st.json(resp_json)
                            
                            # キーの確認
                            st.text(f"レスポンスに含まれるキー: {list(resp_json.keys())}")
                        except:
                            st.text("JSONではないレスポンス:")
                            st.text(response.text[:1000])  # 長すぎる場合は一部のみ表示
                
                # レスポンス確認
                if response.status_code == 200:
                    result = response.json()
                    if "image" in result and result["image"]:
                        # 画像データを保存
                        st.session_state.generated_image = result["image"]
                        st.session_state.last_prompt = prompt
                        st.success("画像が生成されました！")
                    else:
                        keys = list(result.keys()) if isinstance(result, dict) else "なし"
                        st.error(f"画像データがレスポンスに含まれていません。含まれるキー: {keys}")
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
        st.subheader("生成プロンプト")
        st.write(st.session_state.last_prompt)

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
                file_name="gemini_generated_image.png",
                mime="image/png",
                use_container_width=True
            )
        except Exception as img_error:
            st.error(f"画像の表示中にエラーが発生しました: {str(img_error)}")
            st.text(f"画像データの最初の100文字: {st.session_state.generated_image[:100]}...")
    else:
        st.info("プロンプトを入力して「画像を生成」ボタンをクリックしてください")

# app.pyの最後に追加
if __name__ == "__main__":
    # 環境変数PORTの値を取得（デフォルトは8501）
    import os
    port = int(os.environ.get("PORT", 8501))
    # この部分は実際には使用されませんが、デバッグ情報として追加
    print(f"Configured to listen on port {port}")
# フッター
st.markdown("---")
st.markdown("Powered by Google Vertex AI Gemini 2.0")
