
import os
import requests
from flask import Flask, request, abort

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN", ""
)

LINE_API_HEADERS = {
    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


@app.route("/", methods=["GET"])
def home():
    return "LINE 안내봇 실행 중!"


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

        # 신규 멤버 입장 안내
        if event_type == "memberJoined":
            members = event.get(
                "joined", {}
            ).get("members", [])

            names = []

            for member in members:
                user_id = member.get("userId")
                name = get_display_name(
                    user_id, group_id
                )
                names.append(name)

            if not names:
                names = ["신규 멤버"]

            names_text = ", ".join(names)

            message = (
                f"🎉 {names_text} 님이 들어오셨습니다.\n\n"
                "오신 걸 환영합니다! 😊\n"
                "먼저 공지 확인 부탁드립니다.\n\n"
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
                "공지 확인 안내를 전달합니다.\n\n"
                "모두 즐겁게 이용해 주세요! 😊"
            )

            reply_message(reply_token, message)
            continue

        # 기존 텍스트 메시지 응답 유지
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
