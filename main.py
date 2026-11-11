```python
import os
import uuid
import requests
from flask import Flask, request, abort, render_template_string

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN"
)

NOTICE_URL = "https://line-guide-bot.onrender.com/notice"

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

# 투표 데이터: Render 서버가 재시작되면 초기화됨
polls = {}

# 투표 작성 진행 상태
creation_sessions = {}


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
            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">
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


def line_request(endpoint, data):
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("LINE_CHANNEL_ACCESS_TOKEN이 없습니다.")
        return None

    url = "https://api.line.me/v2/bot/message/" + endpoint

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
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
                f"LINE API 오류: "
                f"{response.status_code} {response.text}"
            )

        return response

    except requests.RequestException as error:
        print(f"LINE API 요청 오류: {error}")
        return None


def reply_message(reply_token, text):
    line_request(
        "reply",
        {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
    )


def reply_flex(reply_token, alt_text, contents):
    line_request(
        "reply",
        {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "flex",
                    "altText": alt_text[:400],
                    "contents": contents
                }
            ]
        }
    )


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
            return response.json().get(
                "displayName", "새로운 멤버"
            )

    except requests.RequestException as error:
        print(f"프로필 조회 오류: {error}")

    return "새로운 멤버"


def send_poll(reply_token, poll):
    contents = [
        {
            "type": "text",
            "text": "📊 " + poll["topic"],
            "weight": "bold",
            "size": "xl",
            "wrap": True
        },
        {
            "type": "text",
            "text": (
                "단일 선택"
                if poll["mode"] == "single"
                else "복수 선택"
            ),
            "size": "sm",
            "color": "#888888",
            "margin": "md"
        },
        {
            "type": "separator",
            "margin": "lg"
        }
    ]

    for index, option in enumerate(poll["options"]):
        contents.append({
            "type": "button",
            "style": "primary",
            "color": "#333333",
            "height": "sm",
            "margin": "md",
            "action": {
                "type": "postback",
                "label": option[:20],
                "data": (
                    f"poll:vote:{poll['id']}:{index}"
                ),
                "displayText": option
            }
        })

    if poll["mode"] == "multi":
        contents.append({
            "type": "button",
            "style": "secondary",
            "height": "sm",
            "margin": "lg",
            "action": {
                "type": "postback",
                "label": "선택 완료",
                "data": f"poll:done:{poll['id']}",
                "displayText": "투표 선택 완료"
            }
        })

    contents.append({
        "type": "text",
        "text": "결과 확인: !투표결과",
        "size": "xs",
        "color": "#888888",
        "margin": "lg"
    })

    flex = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": contents
        }
    }

    reply_flex(
        reply_token,
        "📊 " + poll["topic"],
        flex
    )


def poll_result(poll):
    counts = [0] * len(poll["options"])

    for selections in poll["votes"].values():
        for index in selections:
            if 0 <= index < len(counts):
                counts[index] += 1

    total = len(poll["votes"])

    lines = [
        "📊 투표 결과",
        poll["topic"],
        ""
    ]

    for index, option in enumerate(poll["options"]):
        lines.append(
            f"{index + 1}. {option}: {counts[index]}표"
        )

    lines.append("")
    lines.append(f"총 참여자: {total}명")
    lines.append(
        "상태: " + ("종료" if poll["closed"] else "진행 중")
    )

    return "\n".join(lines)


def handle_creation(reply_token, user_id, chat_id, text):
    session = creation_sessions.get(chat_id)

    if not session or session["user_id"] != user_id:
        return False

    stage = session["stage"]

    if stage == "topic":
        if len(text) > 100:
            reply_message(reply_token, "주제는 100자 이내로 입력해 주세요.")
            return True

        session["topic"] = text
        session["stage"] = "mode"

        reply_message(
            reply_token,
            "투표 방식을 선택해 주세요.\n\n"
            "단일 또는 복수라고 입력해 주세요.\n"
            "단일: 한 개만 선택\n"
            "복수: 여러 개 선택"
        )
        return True

    if stage == "mode":
        if text in ["단일", "단일선택"]:
            session["mode"] = "single"
        elif text in ["복수", "복수선택"]:
            session["mode"] = "multi"
        else:
            reply_message(
                reply_token,
                "단일 또는 복수 중 하나를 입력해 주세요."
            )
            return True

        session["stage"] = "options"
        session["options"] = []

        reply_message(
            reply_token,
            "첫 번째 선택 항목을 입력해 주세요."
        )
        return True

    if stage == "options":
        if text.startswith("+항목 "):
            option = text[4:].strip()

            if not option:
                reply_message(reply_token, "항목 내용을 입력해 주세요.")
                return True

            if len(session["options"]) >= 12:
                reply_message(reply_token, "항목은 최대 12개까지 가능합니다.")
                return True

            session["options"].append(option)

            reply_message(
                reply_token,
                f"항목 추가 완료 ({len(session['options'])}/12)\n"
                "+항목 항목내용 : 추가\n"
                "+시작 : 투표 시작"
            )
            return True

        if text == "+시작":
            if len(session["options"]) < 2:
                reply_message(
                    reply_token,
                    "투표 항목은 최소 2개가 필요합니다."
                )
                return True

            poll_id = uuid.uuid4().hex[:10]

            poll = {
                "id": poll_id,
                "topic": session["topic"],
                "mode": session["mode"],
                "options": session["options"],
                "creator": user_id,
                "votes": {},
                "pending": {},
                "closed": False
            }

            polls[chat_id] = poll
            del creation_sessions[chat_id]

            reply_message(
                reply_token,
                "투표를 시작합니다! 아래 투표 버튼을 눌러 주세요."
            )

            # 투표 카드를 별도 답장으로 전송
            # replyToken은 한 번만 사용할 수 있으므로
            # 실제 투표 카드는 아래 Push API로 전송
            push_poll(chat_id, poll)

            return True

        if not session["options"]:
            session["options"].append(text)

            reply_message(
                reply_token,
                "첫 번째 항목이 등록됐습니다.\n"
                "두 번째 선택 항목을 입력해 주세요."
            )
            return True

        if len(session["options"]) == 1:
            session["options"].append(text)

            reply_message(
                reply_token,
                "두 항목이 등록됐습니다.\n\n"
                "+항목 항목내용 : 항목 추가\n"
                "+시작 : 투표 시작\n"
                "최대 12개까지 가능합니다."
            )
            return True

        reply_message(
            reply_token,
            "항목 추가는 '+항목 항목내용' 형식으로 입력해 주세요.\n"
            "투표 시작은 '+시작'입니다."
        )
        return True

    return False


def push_poll(chat_id, poll):
    if not LINE_CHANNEL_ACCESS_TOKEN:
        return

    contents = [
        {
            "type": "text",
            "text": "📊 " + poll["topic"],
            "weight": "bold",
            "size": "xl",
            "wrap": True
        },
        {
            "type": "text",
            "text": (
                "단일 선택"
                if poll["mode"] == "single"
                else "복수 선택"
            ),
            "size": "sm",
            "color": "#888888",
            "margin": "md"
        },
        {
            "type": "separator",
            "margin": "lg"
        }
    ]

    for index, option in enumerate(poll["options"]):
        contents.append({
            "type": "button",
            "style": "primary",
            "color": "#333333",
            "height": "sm",
            "margin": "md",
            "action": {
                "type": "postback",
                "label": option[:20],
                "data": f"poll:vote:{poll['id']}:{index}",
                "displayText": option
            }
        })

    if poll["mode"] == "multi":
        contents.append({
            "type": "button",
            "style": "secondary",
            "height": "sm",
            "margin": "lg",
            "action": {
                "type": "postback",
                "label": "선택 완료",
                "data": f"poll:done:{poll['id']}",
                "displayText": "투표 선택 완료"
            }
        })

    contents.append({
        "type": "text",
        "text": "결과 확인: !투표결과",
        "size": "xs",
        "color": "#888888",
        "margin": "lg"
    })

    flex = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": contents
        }
    }

    data = {
        "to": chat_id,
        "messages": [
            {
                "type": "flex",
                "altText": "📊 " + poll["topic"],
                "contents": flex
            }
        ]
    }

    line_request("push", data)


def handle_postback(event):
    reply_token = event.get("replyToken")
    source = event.get("source", {})
    chat_id = source.get("groupId") or source.get("roomId")
    user_id = source.get("userId")

    if not chat_id or not user_id:
        return

    data = event.get("postback", {}).get("data", "")
    parts = data.split(":")

    if len(parts) < 3 or parts[0] != "poll":
        return

    poll = polls.get(chat_id)

    if not poll or poll["id"] != parts[2]:
        reply_message(reply_token, "해당 투표를 찾을 수 없습니다.")
        return

    if poll["closed"]:
        reply_message(reply_token, "이미 종료된 투표입니다.")
        return

    if parts[1] == "vote":
        if len(parts) != 4:
            return

        try:
            index = int(parts[3])
        except ValueError:
            return

        if index < 0 or index >= len(poll["options"]):
            return

        if poll["mode"] == "single":
            poll["votes"][user_id] = [index]
            reply_message(
                reply_token,
                f"✅ '{poll['options'][index]}' 투표가 완료됐습니다."
            )

        else:
            selected = poll["pending"].setdefault(user_id, [])

            if index in selected:
                selected.remove(index)
                reply_message(
                    reply_token,
                    f"선택 취소: {poll['options'][index]}"
                )
            else:
                selected.append(index)
                reply_message(
                    reply_token,
                    f"선택 완료: {poll['options'][index]}\n"
                    "다른 항목을 선택하거나 '선택 완료'를 눌러 주세요."
                )

    elif parts[1] == "done":
        selected = poll["pending"].get(user_id, [])

        if not selected:
            reply_message(reply_token, "먼저 항목을 선택해 주세요.")
            return

        poll["votes"][user_id] = list(selected)
        del poll["pending"][user_id]

        reply_message(reply_token, "✅ 투표가 완료됐습니다.")


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

        source = event.get("source", {})
        group_id = source.get("groupId")
        room_id = source.get("roomId")
        user_id = source.get("userId")
        chat_id = group_id or room_id

        if not reply_token:
            continue

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
                "명령어: !방장 / !규칙 / !관리자 / !블랙리스트\n"
                "투표 만들기: +투표"
            )

            reply_message(reply_token, message)

        # 투표 버튼 클릭
        elif event_type == "postback":
            handle_postback(event)

        # 일반 메시지
        elif event_type == "message":
            message_event = event.get("message", {})

            if message_event.get("type") != "text":
                continue

            user_message = message_event.get("text", "").strip()

            if not user_id or not chat_id:
                continue

            # 기존 명령어
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
                continue

            # 투표 결과
            if user_message == "!투표결과":
                poll = polls.get(chat_id)

                if not poll:
                    reply_message(reply_token, "현재 진행 중인 투표가 없습니다.")
                else:
                    reply_message(reply_token, poll_result(poll))

                continue

            # 투표 종료
            if user_message == "!투표종료":
                poll = polls.get(chat_id)

                if not poll:
                    reply_message(reply_token, "진행 중인 투표가 없습니다.")
                elif poll["creator"] != user_id:
                    reply_message(reply_token, "투표 작성자만 종료할 수 있습니다.")
                else:
                    poll["closed"] = True
                    reply_message(
                        reply_token,
                        "투표가 종료됐습니다.\n\n"
                        + poll_result(poll)
                    )

                continue

            # 투표 생성 취소
            if user_message == "+취소":
                if chat_id in creation_sessions:
                    if creation_sessions[chat_id]["user_id"] == user_id:
                        del creation_sessions[chat_id]
                        reply_message(reply_token, "투표 만들기를 취소했습니다.")
                    else:
                        reply_message(reply_token, "투표 작성자만 취소할 수 있습니다.")
                else:
                    reply_message(reply_token, "진행 중인 투표 만들기가 없습니다.")

                continue

            # 투표 생성 시작
            if user_message == "+투표":
                if chat_id in creation_sessions:
                    reply_message(reply_token, "이미 투표를 만들고 있습니다.")
                    continue

                creation_sessions[chat_id] = {
                    "user_id": user_id,
                    "stage": "topic",
                    "topic": "",
                    "mode": "",
                    "options": []
                }

                reply_message(
                    reply_token,
                    "📊 투표 만들기를 시작합니다.\n\n"
                    "먼저 투표 주제를 입력해 주세요.\n"
                    "취소하려면 +취소를 입력하세요."
                )
                continue

            # 투표 작성 단계
            if handle_creation(
                reply_token,
                user_id,
                chat_id,
                user_message
            ):
                continue

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
```
