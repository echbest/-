import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

# MediaPipe 설정
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    """세 점 사이의 각도를 계산하는 함수"""
    a = np.array(a) # 첫 번째 점 (예: 엉덩이)
    b = np.array(b) # 중앙 점 (예: 무릎)
    c = np.array(c) # 세 번째 점 (예: 발목)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    return angle

st.title("🏋️ AI 운동 자세 분석기")
st.caption("카메라 앞에서 스쿼트를 해보세요. 무릎 각도를 분석해 드립니다.")

# 스트림릿 사이드바 설정
st.sidebar.title("설정")
threshold = st.sidebar.slider("목표 각도 (정지 상태)", 70, 160, 90)

# 카메라 실행 부분
run = st.checkbox('카메라 시작')
FRAME_WINDOW = st.image([]) # 영상을 보여줄 윈도우

# Pose 모델 초기화
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    cam = cv2.VideoCapture(0)

    while run:
        ret, frame = cam.read()
        if not ret:
            st.error("카메라를 찾을 수 없습니다.")
            break

        # BGR을 RGB로 변환
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # 랜드마크 추출 및 분석
        try:
            landmarks = results.pose_landmarks.landmark
            
            # 엉덩이(24), 무릎(26), 발목(28) 좌표 추출 (왼쪽 기준)
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            # 각도 계산
            angle = calculate_angle(hip, knee, ankle)

            # 피드백 로직
            status = "준비"
            color = (255, 255, 255) # 흰색
            
            if angle < threshold:
                status = "좋습니다! 충분히 내려갔어요."
                color = (0, 255, 0) # 초록색
            elif angle < 160:
                status = "조금 더 내려가 보세요!"
                color = (255, 255, 0) # 노란색

            # 화면에 정보 표시
            cv2.putText(image, f"Angle: {int(angle)}", tuple(np.multiply(knee, [640, 480]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            # 상태 메시지를 앱 화면에 출력
            st.sidebar.metric("현재 무릎 각도", f"{int(angle)}°")
            st.sidebar.write(f"**진단:** {status}")

        except:
            pass

        # 랜드마크 그리기
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Streamlit에 영상 전송
        FRAME_WINDOW.image(image)
    else:
        st.write("카메라가 꺼져 있습니다.")
