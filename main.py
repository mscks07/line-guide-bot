
import os
import requests
from flask import Flask, request, abort

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN", ""
)

@app.route("/", methods=["GET"])
def home():
    return "LINE 안내봇 실행 중!"

@app.route("/callback", methods=["POST"])
def callback():
    if not LINE_CHANNEL_ACCESS_TOKEN:
        abort(500)

    body = request.get_json(silent=True) or {}

    for event in body.get("events", []):
        if event.get("type") != "message":
            continue

        message = event.get("message", {})
        if message.get("type") != "text":
            continue

        reply_token = event.get("replyToken")
        text = message.get("text", "")

        if not reply_token:
            continue

        requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers={
                "Authorization": (
                    f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
                ),
                "Content-Type": "application/json",
            },
            json={
                "replyToken": reply_token,
                "messages": [
                    {"type": "text", "text": f"안녕하세요! 메시지를 확인했어요: {text}"}
                ],
            },
            timeout=10,
        )

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
