import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
import time

st.set_page_config(
    page_title="거시경제 자산배분 & 라이프스타일 시뮬레이터 4.0",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

CHARACTERS = {
    "가치투자자": {
        "name": "오마하의 가치 투자자",
        "desc": "가치주 및 채권 수익률 +1.5% 보너스",
        "icon": "👴",
        "bonus_assets": ["value_stock", "long_bond", "short_bond"],
        "bonus_rate": 0.015
    },
    "퀀트매니저": {
        "name": "올웨더 헤지펀드 매니저",
        "desc": "거시경제 위기 시 손실률 -20% 방어",
        "icon": "📊",
        "defense_buff": 0.8
    },
    "테크엔젤": {
        "name": "실리콘밸리 엔젤 투자자",
        "desc": "기술주 & 가상자산 폭등 시 +3.0% 추가 수익",
        "icon": "🚀",
        "bonus_assets": ["tech_stock", "crypto"],
        "bonus_rate": 0.03
    },
    "트레이더": {
        "name": "월가 모멘텀 트레이더",
        "desc": "단타 미니게임 수익금 1.2배 증폭",
        "icon": "⚡",
        "trading_buff": 1.2
    }
}

ASSETS = {
    "tech_stock": {"name": "대형 기술 성장주 (Tech)", "icon": "💻", "base_vol": 0.18},
    "value_stock": {"name": "가치/배당주 (Value)", "icon": "🏛️", "base_vol": 0.08},
    "defensive_stock": {"name": "필수소비재/방어주", "icon": "🛡️", "base_vol": 0.05},
    "long_bond": {"name": "장기 국채 (20년+)", "icon": "📜", "base_vol": 0.09},
    "short_bond": {"name": "단기 국채 / MMF", "icon": "💵", "base_vol": 0.01},
    "tips": {"name": "물가연동채 (TIPS)", "icon": "⚓", "base_vol": 0.04},
    "gold": {"name": "금 / 귀금속", "icon": "🪙", "base_vol": 0.10},
    "commodity": {"name": "원자재 / 원유", "icon": "🛢️", "base_vol": 0.22},
    "reits": {"name": "글로벌 부동산 리츠", "icon": "🏢", "base_vol": 0.12},
    "crypto": {"name": "가상자산 / 디지털 자산", "icon": "⚡", "base_vol": 0.35}
}

MACRO_SCENARIOS = [
    {
        "name": "1929 대공황 (Great Depression)",
        "desc": "신용 경색과 주식시장 붕괴. 주식 및 원자재 급락, 단기 국채 및 금 강세.",
        "returns": {
            "tech_stock": -0.35, "value_stock": -0.22, "defensive_stock": -0.08,
            "long_bond": 0.08, "short_bond": 0.03, "tips": 0.01,
            "gold": 0.12, "commodity": -0.25, "reits": -0.30, "crypto": -0.50
        }
    },
    {
        "name": "1970년대 스태그플레이션 (Stagflation)",
        "desc": "원유 파동과 고물가+저성장. 주식/채권 동반 하락, 원자재/금/TIPS 급등.",
        "returns": {
            "tech_stock": -0.18, "value_stock": -0.05, "defensive_stock": 0.02,
            "long_bond": -0.12, "short_bond": 0.04, "tips": 0.15,
            "gold": 0.25, "commodity": 0.35, "reits": -0.05, "crypto": -0.10
        }
    },
    {
        "name": "2008 서프라임 금융위기 (Financial Crisis)",
        "desc": "부동산 및 리츠 폭락, 유동성 위기. 안전자산(국채/금) 선호 심리 극대화.",
        "returns": {
            "tech_stock": -0.28, "value_stock": -0.20, "defensive_stock": -0.05,
            "long_bond": 0.14, "short_bond": 0.02, "tips": 0.03,
            "gold": 0.15, "commodity": -0.20, "reits": -0.42, "crypto": -0.40
        }
    },
    {
        "name": "2020 무제한 양적완화 붐 (QE Boom)",
        "desc": "초저금리와 시중 유동성 폭발. 위험자산(기술주, 가상자산, 리츠) 급등.",
        "returns": {
            "tech_stock": 0.40, "value_stock": 0.18, "defensive_stock": 0.08,
            "long_bond": -0.02, "short_bond": 0.01, "tips": 0.05,
            "gold": 0.18, "commodity": 0.15, "reits": 0.25, "crypto": 0.85
        }
    },
    {
        "name": "2022 긴축 & 고금리 쇼크 (Rate Hike Shock)",
        "desc": "인플레이션 잡기 위한 빅스텝 금리 인상. 성장주 및 긴 만기 채권 급락.",
        "returns": {
            "tech_stock": -0.25, "value_stock": 0.04, "defensive_stock": 0.03,
            "long_bond": -0.18, "short_bond": 0.04, "tips": -0.02,
            "gold": -0.03, "commodity": 0.18, "reits": -0.15, "crypto": -0.45
        }
    },
    {
        "name": "2024 AI 산업 혁명 (AI Boom)",
        "desc": "생성형 AI 생태계 폭발적 확장. 기술주 중심 대세 상승장.",
        "returns": {
            "tech_stock": 0.38, "value_stock": 0.12, "defensive_stock": 0.04,
            "long_bond": 0.03, "short_bond": 0.02, "tips": 0.02,
            "gold": 0.08, "commodity": 0.05, "reits": 0.10, "crypto": 0.45
        }
    }
]

LUXURY_ITEMS = [
    {"id": "item1", "name": "롤렉스 서브마리너", "price": 18000000, "pts": 150, "icon": "⌚", "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"},
    {"id": "item2", "name": "맞춤 톰포드 테일러드 수트", "price": 35000000, "pts": 320, "icon": "👔", "img": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400"},
    {"id": "item3", "name": "포르쉐 911 GT3 RS", "price": 280000000, "pts": 2800, "icon": "🏎️", "img": "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?w=400"},
    {"id": "item4", "name": "페라리 SF90 스트라달레", "price": 650000000, "pts": 7000, "icon": "🏎️", "img": "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=400"},
    {"id": "item5", "name": "청담동/한강뷰 펜트하우스", "price": 4500000000, "pts": 50000, "icon": "🏢", "img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400"},
    {"id": "item6", "name": "걸프스트림 G650 비즈니스 전용기", "price": 25000000000, "pts": 300000, "icon": "🛩️", "img": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400"},
    {"id": "item7", "name": "120피트 럭셔리 슈퍼요트", "price": 60000000000, "pts": 800000, "icon": "🛥️", "img": "https://images.unsplash.com/photo-1567899378494-47b22a2ae96a?w=400"},
    {"id": "item8", "name": "몰디브 프라이빗 개인 섬", "price": 150000000000, "pts": 2500000, "icon": "🏝️", "img": "https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=400"}
]

ACHIEVEMENTS = {
    "alchemist": {"title": "【연금술사】", "desc": "총자산 수익률 +100% 달성", "icon": "🧪"},
    "phoenix": {"title": "【불사조】", "desc": "1929 대공황 시나리오에서 수익률 보전", "icon": "🦅"},
    "young_rich": {"title": "【영앤리치】", "desc": "사치품 5개 이상 구매 달성", "icon": "💎"},
    "real_man": {"title": "【상남자】", "desc": "단타 미니게임 올인 승리", "icon": "🔥"},
    "god_hand": {"title": "【초단타 신의 손】", "desc": "단타 연속 3회 누적 수익 50%+", "icon": "⚡"},
    "wallstreet_big": {"title": "【월가의 거물】", "desc": "총자산 100억원 돌파", "icon": "🏛️"},
    "all_rounder": {"title": "【올라운더】", "desc": "10대 자산 모두 투자 보유", "icon": "🌟"}
}

def init_session():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.character = "가치투자자"
        st.session_state.turn = 1
        st.session_state.initial_cash = 100000000
        st.session_state.cash = 100000000
        st.session_state.allocations = {k: 10.0 for k in ASSETS.keys()}
        st.session_state.asset_values = {k: 10000000.0 for k in ASSETS.keys()}
        st.session_state.net_worth_history = [100000000]
        st.session_state.purchased_items = {}
        st.session_state.lifestyle_score = 0
        st.session_state.unlocked_achievements = set()
        st.session_state.equipped_title = "입문 투자자"
        st.session_state.logs = ["시뮬레이터가 시작되었습니다. 초기 자본: 100,000,000원"]
        st.session_state.trading_wins = 0

init_session()

def get_total_asset_value():
    return sum(st.session_state.asset_values.values()) + st.session_state.cash

def get_prestige_class(score):
    if score >= 1000000: return "세계적 부호 (Global Billionaire)"
    if score >= 200000: return "월가의 거물 (Wall St. Titan)"
    if score >= 30000: return "신흥 재벌 (Emerging Tycoon)"
    if score >= 5000: return "강남 자산가 (Gangnam Capitalist)"
    if score >= 500: return "여의도 펀드매니저 (Fund Manager)"
    return "동네 개미 (Individual Retailer)"

def check_achievements():
    total_val = get_total_asset_value()
    roi = ((total_val - st.session_state.initial_cash) / st.session_state.initial_cash) * 100
    
    if roi >= 100:
        st.session_state.unlocked_achievements.add("alchemist")
    if sum(st.session_state.purchased_items.values()) >= 5:
        st.session_state.unlocked_achievements.add("young_rich")
    if total_val >= 10000000000:
        st.session_state.unlocked_achievements.add("wallstreet_big")
    if all(v > 1000000 for v in st.session_state.asset_values.values()):
        st.session_state.unlocked_achievements.add("all_rounder")

st.sidebar.title("👤 투자자 프로필")

char_key = st.sidebar.selectbox(
    "캐릭터 선택",
    options=list(CHARACTERS.keys()),
    format_func=lambda k: f"{CHARACTERS[k]['icon']} {CHARACTERS[k]['name']}"
)
st.session_state.character = char_key
char_info = CHARACTERS[char_key]

st.sidebar.info(f"**특성:** {char_info['desc']}")
st.sidebar.markdown(f"**현재 칭호:** `{st.session_state.equipped_title}`")

total_val = get_total_asset_value()
roi = ((total_val - st.session_state.initial_cash) / st.session_state.initial_cash) * 100

st.sidebar.metric("총 순자산 (Net Worth)", f"{total_val:,.0f} 원", f"{roi:+.2f}%")
st.sidebar.metric("보유 현금 (Cash)", f"{st.session_state.cash:,.0f} 원")
st.sidebar.metric("과시 지수 (Lifestyle Score)", f"{st.session_state.lifestyle_score:,} pt")
st.sidebar.markdown(f"**신분 등급:** ⭐ `{get_prestige_class(st.session_state.lifestyle_score)}`")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 게임 초기화 (Reset Game)"):
    st.session_state.clear()
    init_session()
    st.rerun()

st.title("📈 거시경제 자산배분 & 라이프스타일 시뮬레이터 4.0")
st.caption("경영학과 학업역량 · 데이터 기반 의사결정 · 거시경제 위기관리 세특 탐구 플랫폼")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 포트폴리오 자산배분",
    "🛍️ 럭셔리 상점 & 가라지",
    "⚡ 30초 스피드 단타",
    "🏆 도전과제 & 칭호",
    "📖 세특 보고서 자동생성"
])

# TAB 1: Macro Portfolio Simulation
with tab1:
    st.subheader("🌐 10대 다변화 자산 비중 설정 및 거시경제 시나리오 턴 진행")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🛠️ 자산배분 비중 (총합 100%)")
        new_allocs = {}
        for k, v in ASSETS.items():
            new_allocs[k] = st.slider(
                f"{v['icon']} {v['name']}",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.allocations[k]),
                step=5.0,
                key=f"slider_{k}"
            )
        st.session_state.allocations = new_allocs
        current_sum = sum(new_allocs.values())
        
        if current_sum != 100.0:
            st.warning(f"⚠️ 현재 투자 비중 합계: **{current_sum:.1f}%** (100%에 맞게 자동으로 비중 재조정 후 투자됩니다.)")
        else:
            st.success("✅ 비중 합계 100% 정상 설정됨")
            
        if st.button("🚀 다음 거시경제 턴 진행 (Turn Advance)", use_container_width=True, type="primary"):
            scenario = random.choice(MACRO_SCENARIOS)
            st.session_state.turn += 1
            norm_factor = 100.0 / current_sum if current_sum > 0 else 1.0
            total_investable = sum(st.session_state.asset_values.values())
            
            new_asset_vals = {}
            for k, meta in ASSETS.items():
                alloc_ratio = (st.session_state.allocations[k] * norm_factor) / 100.0
                base_ret = scenario["returns"].get(k, 0.0)
                
                if char_key == "가치투자자" and k in char_info.get("bonus_assets", []):
                    base_ret += char_info["bonus_rate"]
                elif char_key == "테크엔젤" and k in char_info.get("bonus_assets", []) and base_ret > 0:
                    base_ret += char_info["bonus_rate"]
                elif char_key == "퀀트매니저" and base_ret < 0:
                    base_ret *= char_info["defense_buff"]
                    
                prev_val = total_investable * alloc_ratio
                updated_val = prev_val * (1 + base_ret)
                new_asset_vals[k] = max(0, updated_val)
                
            st.session_state.asset_values = new_asset_vals
            new_total = get_total_asset_value()
            st.session_state.net_worth_history.append(new_total)
            
            st.session_state.logs.append(f"**[Turn {st.session_state.turn}]** 시나리오: **{scenario['name']}** 발생! | 총자산: {new_total:,.0f}원")
            check_achievements()
            st.toast(f" Turn {st.session_state.turn}: {scenario['name']} 시나리오 적용 완료!", icon="📈")
            st.rerun()

    with col2:
        st.markdown("### 📊 포트폴리오 파이 차트 & 자산 추이")
        df_pie = pd.DataFrame([
            {"자산": meta["name"], "가치": st.session_state.asset_values[k]}
            for k, meta in ASSETS.items() if st.session_state.asset_values[k] > 0
        ])
        fig_pie = px.pie(df_pie, values="가치", names="자산", hole=0.4, title="현재 자산 포트폴리오 구성")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("### 📈 순자산 성장 라인 그래프")
        df_line = pd.DataFrame({
            "Turn": list(range(1, len(st.session_state.net_worth_history) + 1)),
            "Net Worth": st.session_state.net_worth_history
        })
        fig_line = px.line(df_line, x="Turn", y="Net Worth", markers=True, title="Turn별 누적 순자산 추이 (KRW)")
        st.plotly_chart(fig_line, use_container_width=True)

# TAB 2: Luxury Shop & Garage
with tab2:
    st.subheader("💎 명품 & 사치품 상점 (Luxury Lifestyle Store)")
    shop_cols = st.columns(4)
    for idx, item in enumerate(LUXURY_ITEMS):
        with shop_cols[idx % 4]:
            st.image(item["img"], use_column_width=True)
            st.markdown(f"**{item['icon']} {item['name']}**")
            st.markdown(f"💰 가격: **{item['price']:,.0f} 원**")
            st.markdown(f"✨ 과시 지수: **+{item['pts']:,} pt**")
            owned_count = st.session_state.purchased_items.get(item["id"], 0)
            st.caption(f"보유 수량: {owned_count} 개")
            
            if st.button(f"구매하기", key=f"buy_{item['id']}", use_container_width=True):
                if st.session_state.cash >= item["price"]:
                    st.session_state.cash -= item["price"]
                    st.session_state.purchased_items[item["id"]] = owned_count + 1
                    st.session_state.lifestyle_score += item["pts"]
                    check_achievements()
                    st.success(f"🎉 {item['name']} 구매 성공!")
                    st.rerun()
                else:
                    st.error("❌ 현금이 부족합니다!")

# TAB 3: Speed Day Trading
with tab3:
    st.subheader("⚡ 30초 스피드 단타 미니게임 (Day Trading Blitz)")
    col_t1, col_t2 = st.columns([1, 2])
    with col_t1:
        leverage = st.radio("레버리지 배율", options=[1, 2, 5], format_func=lambda x: f"{x}x 레버리지")
        trade_amount = st.number_input("투입 현금 (원)", min_value=1000000, max_value=int(max(1000000, st.session_state.cash)), value=min(10000000, int(st.session_state.cash)), step=1000000)
        
        if st.button("🚀 매수 (BUY / LONG)", type="primary", use_container_width=True):
            if st.session_state.cash >= trade_amount:
                fluctuation = random.uniform(-0.15, 0.25) * leverage
                if char_key == "트레이더":
                    fluctuation *= char_info["trading_buff"]
                profit = int(trade_amount * fluctuation)
                st.session_state.cash += profit
                st.session_state.net_worth_history.append(get_total_asset_value())
                
                if profit > 0:
                    st.balloons()
                    st.success(f"🚀 떡상 성공! **+{profit:,.0f} 원** 수익!")
                else:
                    st.error(f"📉 떡락... **{profit:,.0f} 원** 손실!")
                check_achievements()

    with col_t2:
        np.random.seed(int(time.time()) % 1000)
        ticks = np.cumsum(np.random.randn(30) * 1.5) + 100
        df_trade = pd.DataFrame({"초(sec)": list(range(1, 31)), "가격 지수": ticks})
        fig_trade = px.line(df_trade, x="초(sec)", y="가격 지수", title="실시간 30초 틱 변동성 차트")
        st.plotly_chart(fig_trade, use_container_width=True)

# TAB 4: Achievements
with tab4:
    st.subheader("🏆 도전과제 및 칭호 관리")
    achieve_cols = st.columns(2)
    for idx, (key, item) in enumerate(ACHIEVEMENTS.items()):
        is_unlocked = key in st.session_state.unlocked_achievements
        with achieve_cols[idx % 2]:
            st.markdown(f"### {item['icon']} {item['title']}")
            st.write(item['desc'])
            if is_unlocked:
                st.success("✅ 달성 완료!")
                if st.button(f"칭호 장착", key=f"equip_{key}"):
                    st.session_state.equipped_title = item['title']
                    st.rerun()

# TAB 5: Report Generator
with tab5:
    st.subheader("📖 대학 입학사정관 제출용 생기부 세특 자동생성기")
    total_val = get_total_asset_value()
    roi = ((total_val - st.session_state.initial_cash) / st.session_state.initial_cash) * 100
    top_asset = max(st.session_state.asset_values, key=st.session_state.asset_values.get)
    
    report_text = f"""[경영 / 경제 / 탐구 세부능력 및 특기사항]

'거시경제 자산배분 시뮬레이션' 프로젝트에서 [{char_info['name']}] 페르소나로 참여하여 10대 글로벌 asset class의 위험 대비 수익률을 모의실험함. 1929 대공황, 스태그플레이션, 긴축 쇼크 등 거시경제 시나리오별 포트폴리오 변동성을 정량 분석함.

[{ASSETS[top_asset]['name']}] 자산을 중심으로 포트폴리오를 최적화하여 최종 수익률 {roi:+.2f}%(총자산 {total_val:,.0f}원)를 달성함. 자산 상승에 따른 과시적 소비(Veblen Effect) 및 과시 지수({st.session_state.lifestyle_score:,}pt) 분석을 경영학적 소비자 행동론과 연계하여 깊이 있는 탐구 보고서를 제출함."""

    st.text_area("📋 자동 생성된 세특 문구", report_text, height=250)
