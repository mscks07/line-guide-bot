```python
import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN"
)

NOTICE_URL = "https://line-guide-bot.onrender.com/notice"

# 명령어와 답변
commands = {
    "!방장": "럭키 165 55 10 경기어딘가",

    "!규칙": (
        "📢 공지를 확인해 주세요!\n\n"
        "공지 확인하기:\n"
        + NOTICE_URL
    ),

    "!관리자": (
        "방장: 럭키\n"
        "부방장: 꽁칠ㄹ"
    ),

    "!블랙리스트": "블랙리스트: tjr",
}


def reply_message(reply_token, message_text):
    """LINE 메시지 답장"""
    url = "https://api.line.me/v2/bot/message/reply"

    headers = {
        "Content-Type": "application/json",
        "Authorization": (
            f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        ),
    }

    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message_text,
            }
        ],
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"LINE 답장 전송 오류: {error}")


def get_display_name(user_id):
    """LINE 사용자 표시 이름 조회"""
    url = (
        "https://api.line.me/v2/bot/profile/"
        + user_id
    )

    headers = {
        "Authorization": (
            f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        ),
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            return response.json().get(
                "displayName", "새로운 멤버"
            )

    except requests.RequestException as error:
        print(f"사용자 이름 조회 오류: {error}")

    return "새로운 멤버"


@app.route("/", methods=["GET"])
def home():
    return "LINE Bot is running!"


@app.route("/notice", methods=["GET"])
def notice():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">
        <title>커뮤니티 공지</title>
    </head>
    <body>
        <h1>🌿 커뮤니티 통합 가이드라인</h1>
        <p>커뮤니티 공지 및 규칙을 확인해 주세요.</p>
    </body>
    </html>
    """)


@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json(silent=True) or {}

    for event in body.get("events", []):
        event_type = event.get("type")

        # 새 멤버 입장
        if event_type == "memberJoined":
            reply_token = event.get("replyToken")

            if not reply_token:
                continue

            members = event.get(
                "joined", {}
            ).get("members", [])

            names = []

            for member in members:
                user_id = member.get("userId")

                if user_id:
                    names.append(
                        get_display_name(user_id)
                    )
                else:
                    names.append("새로운 멤버")

            if names:
                message = (
                    "🎉 "
                    + ", ".join(names)
                    + "님, 환영합니다!\n\n"
                    + "📢 공지를 확인해 주세요.\n"
                    + NOTICE_URL
                )

                reply_message(reply_token, message)

        # 봇이 그룹에 초대되거나 대화방에 참여
        elif event_type == "join":
            reply_token = event.get("replyToken")

            if reply_token:
                message = (
                    "안녕하세요! 🤖\n"
                    "공지와 명령어를 확인해 주세요.\n\n"
                    + NOTICE_URL
                )

                reply_message(reply_token, message)

        # 일반 텍스트 명령어
        elif event_type == "message":
            message_data = event.get(
                "message", {}
            )

            if message_data.get("type") != "text":
                continue

            user_message = message_data.get(
                "text", ""
            ).strip()

            reply_token = event.get("replyToken")

            if not reply_token:
                continue

            if user_message in commands:
                reply_message(
                    reply_token,
                    commands[user_message],
                )

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
```
