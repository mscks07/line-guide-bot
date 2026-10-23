
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

def reply_message(reply_token, text):
    return requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers={
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "replyToken": reply_token,
            "messages": [
                {"type": "text", "text": text}
            ],
        },
        timeout=10,
    )

@app.route("/callback", methods=["POST"])
def callback():
    if not LINE_CHANNEL_ACCESS_TOKEN:
        abort(500)

    body = request.get_json(silent=True) or {}

    for event in body.get("events", []):
        event_type = event.get("type")
        reply_token = event.get("replyToken")

        if not reply_token:
            continue

        # 새로운 멤버가 그룹방에 입장한 경우
        if event_type == "memberJoined":
            message = (
                "🎉 새로운 멤버가 입장했어요!\n\n"
                "👋 환영합니다! 안내봇입니다.\n\n"
                "📌 [그룹 안내]\n"
                "이 그룹의 목적과 공지사항을 확인해 주세요.\n\n"
                "📖 [이용 규칙]\n"
                "1. 서로 예의를 지켜 주세요.\n"
                "2. 상대방의 개인정보를 무단으로 공유하지 마세요.\n"
                "3. 광고와 도배는 금지합니다.\n"
                "4. 불편한 상황은 관리자에게 알려 주세요.\n\n"
                "모두 즐겁게 이용해 주세요! 😊"
            )
            reply_message(reply_token, message)
            continue

        # 봇이 그룹방에 처음 초대된 경우
        if event_type == "join":
            message = (
                "안녕하세요! 🤖 안내봇입니다.\n\n"
                "그룹 안내와 이용 규칙을 전달해 드릴게요.\n"
                "새 멤버가 입장하면 환영 및 규칙 안내를 보냅니다.\n\n"
                "관리자 공지를 확인하고 서로 존중하며 이용해 주세요!"
            )
            reply_message(reply_token, message)
            continue

        # 기존 텍스트 메시지 응답 기능 유지
        if event_type != "message":
            continue

        incoming = event.get("message", {})

        if incoming.get("type") != "text":
            continue

        text = incoming.get("text", "")

        reply_message(
            reply_token,
            f"안녕하세요! 메시지를 확인했어요: {text}"
        )

    return "OK"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
