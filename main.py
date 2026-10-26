
from flask import Flask, request, abort, render_template_string
import os
import requests

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

NOTICE_URL = "https://line-guide-bot.onrender.com/notice"

IMAGE_URL = (
    "https://raw.githubusercontent.com/mscks07/line-guide-bot/"
    "main/867569186_972749505893600_799013672998306805_n.jpg"
)

NOTICE_CONTENT = """🌿 커뮤니티 통합 가이드라인

본 가이드라인은 쾌적하고 건강한 대화 환경을 유지하기 위해 작성되었습니다. 모든 서버 구성원은 본 규칙을 반드시 숙지해 주시기 바라며, 위반 시 조치가 취해질 수 있습니다.

1. 미활동 및 인원 관리
1-1. 미활동 기준: 대화에 참여하지 않고 장기간 관망(눈팅)만 하는 경우 미활동 인원으로 간주합니다.
1-2. 미활동 조치: 원활한 서버 관리 및 유령 회원 정리를 위해 사전 통보 없이 경고 또는 강제 퇴장(내보내기) 조치가 진행될 수 있습니다.

2. 언행 및 대화 매너 (선을 넘는 대화 금지)
2-1. 불쾌감 유발 금지: 자극적인 플러팅, 가스라이팅, 과도한 비하/조롱 등 타인에게 불쾌감을 줄 수 있는 모든 언행을 엄격히 금지합니다.
2-2. 몰상식한 행동 금지: 서버 분위기를 해치는 상식 밖의 행위(공격성 분탕, 도배, 선동 등)는 발견 즉시 제재됩니다.

3. 개인 메세지(갠뎀/DM) 및 하위 그룹 생성 관련
3-1. 개인 간 분쟁 금지: 개인 메시지(DM)를 통한 다툼으로 인해 인원이 이탈할 경우, 원인 규명을 위한 조사가 진행될 수 있습니다.
3-2. DM 전환 시 은밀한 사적 조작 및 공작 행위 적발 시 엄중 조
3-3. 사적 하위 그룹방 생성 금지: 운영진의 허가 없이 임의로 파벌성 그룹 대화방을 생성하는 행위는 엄격히 금지합니다.

4. 블랙리스트 및 연좌제 관련
4-1. 블랙리스트 접촉 금지: 서버 블랙리스트 지정 인원과의 직접적인 교류 및 본 서버로의 유입/접촉 시도를 금지합니다. (상황 공유 등)
4-2. 연좌 처분: 블랙리스트 인원과 친분을 유지하며 서버 내 악영향을 미치는 인원 역시 동일하게 블랙리스트 처분됩니다.
4-3. 블랙리스트 관련: 뭐 때문이냐고 블랙리스트 인원한테 가서 물어보지도 마세요

5. 알림 설정 안내 및 기타
5-1. 알림 설정: 메시지 알림이 과도하게 느껴질 경우, 서버 알림을 끄세요.
5-2. 문의 및 제보: 가이드라인 위반 행위를 목격하거나 문의 사항이 있으신 경우, 채팅방에 !관리자 전송 후 관리자에게 DM으로 제보해 주세요.
"""


@app.route("/")
def home():
    return "LINE 안내봇 실행 중!"


@app.route("/notice")
def notice():
    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>커뮤니티 통합 가이드라인</title>
            <style>
                body {
                    font-family: sans-serif;
                    line-height: 1.7;
                    max-width: 800px;
                    margin: 30px auto;
                    padding: 0 20px;
                    white-space: pre-wrap;
                    overflow-wrap: break-word;
                }
            </style>
        </head>
        <body>{{ content }}</body>
        </html>
        """,
        content=NOTICE_CONTENT
    )


def reply_message(reply_token, text):
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("오류: LINE_CHANNEL_ACCESS_TOKEN 환경 변수가 설정되지 않았습니다.")
        return

    url = "https://api.line.me/v2/bot/message/reply"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }

    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"LINE 답장 전송 실패: "
                f"{response.status_code} {response.text}"
            )

    except requests.RequestException as error:
        print(f"LINE API 요청 오류: {error}")


def reply_image(reply_token):
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("오류: LINE_CHANNEL_ACCESS_TOKEN 환경 변수가 설정되지 않았습니다.")
        return

    url = "https://api.line.me/v2/bot/message/reply"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }

    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": IMAGE_URL,
                "previewImageUrl": IMAGE_URL
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code != 200:
            print(
                f"사진 전송 실패: "
                f"{response.status_code} {response.text}"
            )

    except requests.RequestException as error:
        print(f"사진 전송 요청 오류: {error}")


def get_display_name(user_id, group_id=None):
    if not LINE_CHANNEL_ACCESS_TOKEN or not user_id:
        return "새로운 멤버"

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }

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
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json().get("displayName", "새로운 멤버")

        print(
            f"프로필 조회 실패: "
            f"{response.status_code} {response.text}"
        )

    except requests.RequestException as error:
        print(f"프로필 조회 오류: {error}")

    return "새로운 멤버"


@app.route("/callback", methods=["POST"])
def callback():
    if not request.is_json:
        abort(400)

    body = request.get_json(silent=True)

    if not body:
        abort(400)

    for event in body.get("events", []):
        event_type = event.get("type")
        reply_token = event.get("replyToken")

        if not reply_token:
            continue

        source = event.get("source", {})
        group_id = source.get("groupId")

        # 새 멤버 입장
        if event_type == "memberJoined":
            members = event.get("joined", {}).get("members", [])

            names = [
                get_display_name(member.get("userId"), group_id)
                for member in members
            ]

            if names:
                names_text = ", ".join(names)

                message = (
                    f"🌿 {names_text}님, 환영합니다!\n\n"
                    "입장하셨다면 아래 공지를 꼭 확인해 주세요.\n"
                    f"{NOTICE_URL}"
                )

                reply_message(reply_token, message)

        # 봇이 그룹에 초대됨
        elif event_type == "join":
            message = (
                "안녕하세요! 🌿\n"
                "저는 커뮤니티 안내봇입니다.\n\n"
                "공지와 규칙은 아래 링크에서 확인해 주세요.\n"
                f"{NOTICE_URL}\n\n"
                "명령어: !방장 / !규칙 / !관리자 / !블랙리스트 / !꽁칠ㄹ"
            )

            reply_message(reply_token, message)

        # 명령어 응답
        elif event_type == "message":
            message_event = event.get("message", {})

            if message_event.get("type") != "text":
                continue

            user_message = message_event.get("text", "").strip()

            # 사진 전송 명령어
            if user_message == "!꽁칠ㄹ":
                reply_image(reply_token)
                continue

            commands = {
                "!방장": "럭키 165 55 10 경기어딘가",

                "!규칙": (
                    "📢 공지를 확인해 주세요!\n\n"
                    "공지 확인하기:\n"
                    f"{NOTICE_URL}"
                ),

                "!관리자": (
                    "방장: 럭키\n"
                    "부방장: 꽁칠ㄹ"
                ),

                "!블랙리스트": "블랙리스트: tjr"
            }

            if user_message in commands:
                reply_message(
                    reply_token,
                    commands[user_message]
                )

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
