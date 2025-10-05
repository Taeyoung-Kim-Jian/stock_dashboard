# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from supabase import create_client

# ------------------------------------------------
# 환경 변수 및 Supabase 연결 (Render + Streamlit Cloud 겸용)
# ------------------------------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Supabase 환경변수(SUPABASE_URL, SUPABASE_KEY)가 설정되지 않았습니다.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------------------------------------
# 페이지 설정
# ------------------------------------------------
st.set_page_config(page_title="스윙 종목 대시보드", layout="wide")

# ------------------------------------------------
# 상단 네비게이션 (아이콘 형태)
# ------------------------------------------------
st.markdown("""
<style>
.top-nav {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 6px 0;
  background-color: #f8f9fa;
  border-radius: 10px;
  margin-bottom: 12px;
}
.nav-btn {
  text-decoration: none;
  padding: 6px 12px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  color: #333;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
}
.nav-btn:hover {
  background: #ffb74d;
  color: white;
  transform: scale(1.05);
}
</style>

<div class="top-nav">
  <a href="#" class="nav-btn">🇰🇷 국내눌림</a>
  <a href="#" class="nav-btn">🇰🇷 국내추격</a>
  <a href="#" class="nav-btn">🌎 해외눌림</a>
  <a href="#" class="nav-btn">🌎 해외추격</a>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# 제목
# ------------------------------------------------
st.markdown("<h4 style='text-align:center;'>💹 스윙 종목 TOP5 대시보드</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:13px; color:gray;'>카테고리를 선택하여 세부 정보를 확인하세요.</p>", unsafe_allow_html=True)
st.markdown("---")

# ------------------------------------------------
# 데이터 로딩
# ------------------------------------------------
@st.cache_data(ttl=300)
def load_returns():
    query = (
        supabase.table("b_return")
        .select("종목명, 종목코드, 수익률, 발생일, 구분")
        .order("수익률", desc=True)
        .limit(5000)
    )
    res = query.execute()
    return pd.DataFrame(res.data)

df_all = load_returns()
if df_all.empty:
    st.warning("⚠️ Supabase의 b_return 테이블에 데이터가 없습니다.")
    st.stop()

# ------------------------------------------------
# 데이터 구성
# ------------------------------------------------
df_all["수익률"] = df_all["수익률"].astype(float)
domestic_top5 = df_all.sort_values("수익률", ascending=False).head(5).reset_index(drop=True)
domestic_bottom5 = df_all.sort_values("수익률", ascending=True).head(5).reset_index(drop=True)

foreign_top5 = pd.DataFrame({
    "종목명": ["Apple", "Nvidia", "Microsoft", "Tesla", "Amazon"],
    "수익률": [15.4, 13.2, 11.8, 10.6, 9.9]
})
foreign_bottom5 = pd.DataFrame({
    "종목명": ["Intel", "Cisco", "AT&T", "Pfizer", "IBM"],
    "수익률": [-3.5, -4.1, -5.0, -6.8, -8.2]
})

# ------------------------------------------------
# 카드 CSS
# ------------------------------------------------
st.markdown("""
<style>
body, div, p {
    font-family: 'Noto Sans KR', sans-serif;
}
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 16px;
    width: 100%;
}
.card {
    background: linear-gradient(135deg, #fff8cc, #ffd966);
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    transition: transform 0.15s ease, box-shadow 0.25s ease;
}
.card:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
}
.card-title {
    font-size: 15px;
    font-weight: 800;
    color: #b35a00;
    margin-bottom: 8px;
    text-align: center;
}
.card-item {
    font-size: 13px;
    color: #333;
    padding: 3px 0;
    border-bottom: 1px dashed rgba(0,0,0,0.1);
}
.card-item b {
    color: #c75000;
}
.card-item span {
    float: right;
    color: #333;
    font-weight: 600;
}
@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .card { padding: 10px; }
    .card-item { font-size: 12px; }
}
footer {visibility: hidden;}
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# 카드 생성 함수
# ------------------------------------------------
def make_card(title, df):
    html = f"<div class='card'><div class='card-title'>{title}</div>"
    for i, row in df.iterrows():
        html += f"<div class='card-item'><b>{i+1}위. {row['종목명']}</b><span>{row['수익률']:.2f}%</span></div>"
    html += "</div>"
    return html

# ------------------------------------------------
# 카드 표시
# ------------------------------------------------
cards_html = f"""
<div class='dashboard-grid'>
    {make_card("🇰🇷 국내 눌림 상위 TOP5", domestic_top5)}
    {make_card("🇰🇷 국내 눌림 하위 TOP5", domestic_bottom5)}
    {make_card("🌎 해외 성장 상위 TOP5", foreign_top5)}
    {make_card("🌎 해외 성장 하위 TOP5", foreign_bottom5)}
</div>
"""
st.markdown(cards_html, unsafe_allow_html=True)

# ------------------------------------------------
# 하단 안내
# ------------------------------------------------
st.markdown("---")
st.caption("💡 Render/Streamlit Cloud 모두에서 정상 동작하도록 구성되었습니다. (PC: 4단 / 모바일: 2단 자동 조정)")
