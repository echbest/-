import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

# 1. 초기 설정
st.set_page_config(page_title="AI 운동 분석기", layout="wide")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# 각도 계산 함수
def get_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# 2. UI 화면 구성
st.title("🏋️ AI 실시간 운동 피드백")
st.subheader("카메라를 켜고 스쿼트 자세를 취해보세요!")

col1, col2 = st.columns([3, 1])

with col2:
    st.write("### 📢 분석 결과")
    status_text = st.empty()
    angle_text = st.empty()
    st.info("무릎 각도가 90도 이하로 내려가면 '굿!' 표시가 뜹니다.")

# 3. 카메라 실행 로직
run = st.checkbox('카메라 켜기/끄기')
FRAME_WINDOW = col1.image([])

# 카메라 캡처 시작
cap = cv2.VideoCapture(0)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while run:
        ret, frame = cap.read()
        if not ret:
            st.error("카메라를 불러올 수 없습니다.")
            break

        # 처리 효율을 위해 이미지 변환
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # 랜드마크(관절 포인트)가 발견되면
        if results.pose_landmarks:
            try:
                landmarks = results.pose_landmarks.landmark
                
                # 왼쪽 무릎 각도 계산용 좌표 (힙, 무릎, 발목)
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                
                angle = get_angle(hip, knee, ankle)

                # 각도에 따른 피드백
                if angle < 90:
                    status = "✅ 완벽한 깊이입니다! (Good)"
                    color = (0, 255, 0)
                elif angle < 140:
                    status = "🟡 조금 더 내려가보세요!"
                    color = (255, 255, 0)
                else:
                    status = "🧍 서 있는 상태입니다."
                    color = (255, 255, 255)

                # 결과 업데이트
                status_text.markdown(f"**현재 상태:** {status}")
                angle_text.metric("무릎 각도", f"{int(angle)}°")

                # 화면에 관절 선 그리기
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
            except Exception as e:
                pass

        # 화면 출력
        FRAME_WINDOW.image(image)

    cap.release()
