import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 웹사이트 제목 설정
st.set_page_config(page_title="고교 스포츠 부상 예측 시스템", page_icon="🏃‍♂️")
st.title("🏃‍♂️ 고교 체육 선수를 위한 부상 위험도 예측 대시보드")
st.write("스포츠 과학 이론(ACWR)을 적용하여 선수의 훈련량과 생체 데이터를 분석합니다.")
st.markdown("---")

# 1. 데이터 입력창 (사이드바)
st.sidebar.header("📋 오늘의 데이터 입력")
duration = st.sidebar.slider("⏱ 오늘 운동 시간 (분)", 0, 180, 90)
rpe = st.sidebar.slider("🏋️‍♂️ 오늘 운동 강도 (RPE, 1~10)", 1, 10, 6)
sleep = st.sidebar.slider("😴 전날 수면 시간 (시간)", 4.0, 10.0, 7.5, step=0.5)

# 2. 이과적 데이터 계산 (수학적 모델링)
today_load = duration * rpe  # 오늘의 훈련 부하

# 가상의 지난 3주 데이터 (원래 데이터가 누적되어야 계산되므로 가상으로 만듦)
np.random.seed(42)
past_loads = np.random.randint(300, 600, size=21)
acute_load = (past_loads[-6:].sum() + today_load) / 7  # 최근 1주일 평균 (피로도)
chronic_load = (past_loads.sum() + today_load) / 22    # 최근 3주일 평균 (체력)
acwr = round(acute_load / chronic_load, 2)            # 급성/만성 훈련 비율

# 3. 화면에 결과 보여주기
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="오늘의 훈련 부하", value=f"{today_load} 점")
with col2:
    if 0.8 <= acwr <= 1.3:
        st.metric(label="부상 위험 지수(ACWR)", value=f"{acwr}", delta="안전 (Sweet Spot)")
    elif acwr > 1.3:
        st.metric(label="부상 위험 지수(ACWR)", value=f"{acwr}", delta="위험 (오버트레이닝!!)", delta_color="inverse")
    else:
        st.metric(label="부상 위험 지수(ACWR)", value=f"{acwr}", delta="경고 (과소훈련)")
with col3:
    st.metric(label="목표 수면 달성도", value=f"{int(sleep/8*100)}%", delta=f"{sleep}시간")

st.markdown("---")
st.subheader("📊 최근 훈련 부하 변화 그래프")

# 그래프용 데이터 가공 및 시각화
df = pd.DataFrame({"날짜": [f"D-{21-i}" for i in range(21)] + ["오늘"], "훈련부하": list(past_loads) + [today_load]})
fig = px.line(df, x="날짜", y="훈련부하", markers=True, title="일자별 훈련량 추이")
st.plotly_chart(fig, use_container_width=True)

# 4. 생기부용 이론 설명 설명창
with st.expander("💡 [생기부용 전공 지식] ACWR 이란?"):
    st.write("급성/만성 훈련 부하 비율(Acute:Chronic Workload Ratio)의 약자로, 프로 구단에서 부상 방지를 위해 사용하는 실제 스포츠 과학 공식입니다. 최근 1주간의 운동량(급성)을 한 달간의 평균 운동량(만성)으로 나눈 값이며, 이 비율이 1.5를 넘어가면 부상 확률이 급격히 증가합니다.")
