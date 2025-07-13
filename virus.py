import streamlit as st
import numpy as np
from scipy.stats import beta
import plotly.graph_objs as go

# ----------------------
# 고등학생 눈높이 설명
# ----------------------
# 이 시뮬레이션은 코로나 감염률을 베이지안 방식(베타 분포)으로 예측합니다.
# 베타 분포는 감염률(0~1 사이 값)에 대한 확률을 나타내는 분포입니다.
# 매일 관찰된 감염자 수를 입력하면, 그 정보를 반영해 감염률에 대한 믿음(분포)이 업데이트됩니다.

st.title("코로나 감염률 베이지안 예측 시뮬레이션")

# 1. 입력 파라미터
st.sidebar.header("시뮬레이션 파라미터")
alpha = st.sidebar.slider("초기 α (감염자 수에 대한 믿음)", 1, 20, 2)
beta_param = st.sidebar.slider("초기 β (비감염자 수에 대한 믿음)", 1, 20, 18)
population = st.sidebar.slider("총 인구 수", 1000, 10000, 5000)

# --- 베타 분포 설명 (사이드바 하단) ---
st.sidebar.markdown("""
---
**[베타 분포와 파라미터 설명]**
- **베타 분포**: 0~1 사이의 값(예: 감염률)에 대한 믿음을 곡선으로 표현하는 확률분포입니다.
- **α(알파)**: 감염자 수에 대한 믿음 (관찰된 감염자 수 + 초기 가정)
- **β(베타)**: 비감염자 수에 대한 믿음 (관찰된 비감염자 수 + 초기 가정)
- α, β 값이 클수록 해당 집단(감염자/비감염자)이 많을 것이라는 믿음이 강해집니다.
- 예시: α=2, β=18이면 감염자 2명, 비감염자 18명을 관찰했다고 가정한 것과 같습니다.

> **감염률에 대한 믿음이란?**\
> 실제 감염률이 얼마일지에 대해 우리가 가지고 있는 불확실한 추정(확률분포)입니다.\
> 검사 데이터가 많아질수록 이 곡선은 더 뾰족해집니다 (확신이 커짐).
""")

# 2. 일별 감염자 입력
st.subheader("일별 신규 감염자 수 입력 (7일)")
day1 = st.number_input("1일차 감염자 수", min_value=0, value=2)
day2 = st.number_input("2일차 감염자 수", min_value=0, value=5)
day3 = st.number_input("3일차 감염자 수", min_value=0, value=4)
day4 = st.number_input("4일차 감염자 수", min_value=0, value=3)
day5 = st.number_input("5일차 감염자 수", min_value=0, value=6)
day6 = st.number_input("6일차 감염자 수", min_value=0, value=5)
day7 = st.number_input("7일차 감염자 수", min_value=0, value=7)

# 검사자 수(고정)
tested_per_day = st.sidebar.slider("매일 검사한 사람 수", 10, 500, 100)

# 3. 시뮬레이션 및 시각화
if st.button("예측 시작"):
    observed = [day1, day2, day3, day4, day5, day6, day7]
    alpha_list = [alpha]
    beta_list = [beta_param]
    mean_list = [alpha / (alpha + beta_param)]
    ci_low = []
    ci_high = []
    x = np.linspace(0, 1, 200)

    # plotly 그래프 준비
    fig = go.Figure()
    y = beta.pdf(x, alpha, beta_param)
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f"Day 0 (Prior)"))

    # 단계별 업데이트
    a, b = alpha, beta_param
    for i, cases in enumerate(observed):
        a += cases
        b += tested_per_day - cases
        alpha_list.append(a)
        beta_list.append(b)
        mean = a / (a + b)
        mean_list.append(mean)
        # 95% 신뢰구간
        ci = beta.interval(0.95, a, b)
        ci_low.append(ci[0])
        ci_high.append(ci[1])
        y = beta.pdf(x, a, b)
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f"Day {i+1}"))

    fig.update_layout(
        title="베타 분포로 본 감염률에 대한 믿음 변화",
        xaxis_title="감염률 (0~1)",
        yaxis_title="확률밀도",
        legend_title="Day"
    )
    st.plotly_chart(fig, use_container_width=True)

    # 4. 결과 요약
    st.subheader("7일 후 감염률 예측 결과")
    st.write(f"베타 분포 평균(점 추정): {mean_list[-1]:.4f}")
    st.write(f"95% 신뢰구간: [{ci_low[-1]:.4f}, {ci_high[-1]:.4f}]")
    st.write(f"예상 감염자 수: {int(mean_list[-1] * population)}명 / {population}명")

    # (선택) 각 단계별 평균 변화 그래프 (plotly)
    days = list(range(8))
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=days, y=mean_list, mode='lines+markers', name='감염률 평균'))
    fig2.add_trace(go.Scatter(
        x=days[1:] + days[:0:-1],
        y=ci_high + ci_low[::-1],
        fill='toself',
        fillcolor='rgba(128,128,128,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='95% 신뢰구간',
    ))
    fig2.update_layout(
        title='일별 감염률 평균 및 신뢰구간',
        xaxis_title='Day',
        yaxis_title='감염률',
        legend_title='범례'
    )
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------
# (참고) 베타 분포란?
# ----------------------
# 베타 분포는 0~1 사이의 확률(예: 감염률)에 대한 믿음을 표현하는 분포입니다.
# α, β 값이 클수록 분포가 뾰족해지고, 작을수록 퍼집니다.
# 관찰 데이터(감염자 수)가 추가될 때마다 α, β가 업데이트되어 분포가 바뀝니다.