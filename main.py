
import os
import requests
from flask import Flask, request, abort, render_template_string

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN", ""
)

LINE_API_HEADERS = {
    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# ==================================
# 나중에 이 부분의 공지 내용만 수정
# ==================================
NOTICE_CONTENT = """
📢 그룹 공지사항

공지 내용은 나중에 이 부분에서 수정하면 됩니다.

1. 공지사항을 먼저 확인해 주세요.
2. 공지 확인 후 자기소개와 사진을 업로드해 주세요.
3. 서로 예의를 지켜 주세요.
4. 광고와 도배는 금지합니다.
5. 다른 사람의 개인정보를 무단으로 공유하지 마세요.
"""


@app.route("/", methods=["GET"])
def home():
    return "LINE 안내봇 실행 중!"


# 공지 전용 웹페이지
@app.route("/notice", methods=["GET"])
def notice():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        <title>그룹 공지사항</title>
        <style>
            body {
                font-family: sans-serif;
                max-width: 700px;
                margin: 0 auto;
                padding: 24px 18px;
                line-height: 1.8;
                background: #f7f7f7;
                color: #222;
            }
            main {
                background: white;
                padding: 24px;
                border-radius: 14px;
                white-space: pre-wrap;
                overflow-wrap: anywhere;
            }
            h1 {
                font-size: 24px;
                margin-top: 0;
            }
        </style>
    </head>
    <body>
        <main>
            <h1>📢 그룹 공지사항</h1>
            {{ content }}
        </main>
    </body>
    </html>
    """, content=NOTICE_CONTENT)


def reply_message(reply_token, text):
    return requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=LINE_API_HEADERS,
        json={
            "replyToken": reply_token,
            "messages": [
                {"type": "text", "text": text}
            ],
        },
        timeout=10,
    )


def get_display_name(user_id, group_id=None):
    if not user_id:
        return "신규 멤버"

    if group_id:
        url = (
            "https://api.line.me/v2/bot/group/"
            f"{group_id}/member/{user_id}"
        )
    else:
        url = (
            "https://api.line.me/v2/bot/profile/"
            f"{user_id}"
        )

    try:
        response = requests.get(
            url,
            headers=LINE_API_HEADERS,
            timeout=10,
        )

        if response.ok:
            return response.json().get(
                "displayName", "신규 멤버"
            )
    except requests.RequestException:
        pass

    return "신규 멤버"


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

        source = event.get("source", {})
        group_id = source.get("groupId")

        # 신규 멤버 입장
        if event_type == "memberJoined":
            members = event.get(
                "joined", {}
            ).get("members", [])

            names = [
                get_display_name(
                    member.get("userId"), group_id
                )
                for member in members
            ]

            if not names:
                names = ["신규 멤버"]

            message = (
                f"🎉 {', '.join(names)} 님이 들어오셨습니다.\n\n"
                "오신 걸 환영합니다! 😊\n"
                "먼저 공지 확인 부탁드립니다.\n\n"
                "📢 공지 확인하기:\n"
                "https://line-guide-bot.onrender.com/notice\n\n"
                "공지 확인 후 자기소개와 사진을 "
                "업로드해 주세요."
            )

            reply_message(reply_token, message)
            continue

        # 봇이 그룹에 초대된 경우
        if event_type == "join":
            message = (
                "안녕하세요! 🤖 안내봇입니다.\n\n"
                "신규 멤버 입장 시 환영 인사와 "
                "공지 링크를 안내합니다.\n\n"
                "📢 그룹 공지 확인하기:\n"
                "https://line-guide-bot.onrender.com/notice\n\n"
                "모두 즐겁게 이용해 주세요! 😊"
            )

            reply_message(reply_token, message)
            continue

        # 기존 텍스트 메시지 응답
        if event_type == "message":
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
