# 以下を「app.py」に書き込み
import streamlit as st
import openai
import numpy as np
import pandas as pd
import hmac
import requests
import hashlib
import json
from datetime import datetime, timezone
import streamlit.components.v1 as stc
import base64
import time

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "あなたは優秀なアシスタントAIです。"}
        ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )  

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去


    
# 声変換
def texttospeech(input_text):
  accesskey = 'TwCIh2tDPWJtujihLZ40paTWM'
  access_secret = 'sJg7bnYeCTraHJlZmerIaepXOihaJvAMjKiZ0eEp'

  text = input_text
  date: str = str(int(datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()))
  data: str = json.dumps({
    'coefont': '2b174967-1a8a-42e4-b1ae-5f6548cfa05d',
    'text': text
  })
  signature = hmac.new(bytes(access_secret, 'utf-8'), (date+data).encode('utf-8'), hashlib.sha256).hexdigest()

  response = requests.post('https://api.coefont.cloud/v2/text2speech', data=data, headers={
    'Content-Type': 'application/json',
    'Authorization': accesskey,
    'X-Coefont-Date': date,
    'X-Coefont-Content': signature
  })

  if response.status_code == 200:
    with open('response.wav', 'wb') as f:
      f.write(response.content)
  else:
    print(response.json())
  st.sidebar.write("声変換完了")



# ユーザーインターフェイスの構築
st.title("My AI Assistant")
st.write("ChatGPT APIを使ったチャットボットです。")

user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]

    for message in reversed(messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂"
        if message["role"]=="assistant":
            speaker="🤖"

        st.write(speaker + ": " + message["content"])


# ---------- サイドバー ----------
st.sidebar.title("CoeFont")

if st.sidebar.button("声変換", key=0):
  texttospeech(st.session_state["messages"][-1]["content"])
  
if st.sidebar.button("声再生", key=1):
  audio_path1 = 'response.wav' #入力する音声ファイル

  audio_placeholder = st.empty()

  file_ = open(audio_path1, "rb")
  contents = file_.read()
  file_.close()

  audio_str = "data:audio/ogg;base64,%s"%(base64.b64encode(contents).decode())
  audio_html = """
                  <audio autoplay=True>
                  <source src="%s" type="audio/ogg" autoplay=True>
                  Your browser does not support the audio element.
                  </audio>
              """ %audio_str

  audio_placeholder.empty()
  time.sleep(0.5) #これがないと上手く再生されません
  audio_placeholder.markdown(audio_html, unsafe_allow_html=True)

        
       
