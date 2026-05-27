import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit ADoFaI - Guide Mode", layout="centered")

# 난이도 세팅
themes = {
    "Easy": {
        "bg": "#050806", "sidebar_bg": "#0D140F", "text": "#E0F2F1",
        "speed": 0.05, "tolerance": 0.30
    },
    "Normal": {
        "bg": "#141008", "sidebar_bg": "#1F180D", "text": "#FFF8E1",
        "speed": 0.08, "tolerance": 0.20
    },
    "Hard": {
        "bg": "#050B14", "sidebar_bg": "#0A1424", "text": "#E3F2FD",
        "speed": 0.13, "tolerance": 0.12
    }
}

st.sidebar.header("🕹️ 게임 설정")
difficulty = st.sidebar.selectbox("난이도 선택", ["Easy", "Normal", "Hard"])
theme = themes[difficulty]

# 동적 테마 CSS 적용
custom_css = f"""
<style>
    .stApp {{ background-color: {theme['bg']} !important; color: {theme['text']} !important; }}
    [data-testid="stSidebar"] {{ background-color: {theme['sidebar_bg']} !important; }}
    h1, h2, h3, p, span, label, .stMarkdown {{ color: {theme['text']} !important; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.title("🔥 🧊 얼불춤: 하이라이트 가이드 모드")
st.write(f"현재 모드: **{difficulty}** | 초록색으로 빛나는 다음 타일을 조준하세요!")
st.info("⚠️ 게임 화면(검은 캔버스)을 **클릭**한 후 스페이스바를 누르세요!")

# 가이드 라인 및 초록색 하이라이트 기능이 추가된 엔진
game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background-color: {theme['bg']}; color: {theme['text']}; text-align: center; font-family: sans-serif; margin: 0; padding: 0; overflow: hidden; }}
        canvas {{ background: #0a0a0a; border: 3px solid #555; display: block; margin: 0 auto; border-radius: 8px; box-shadow: 0 0 30px rgba(255,255,255,0.05); }}
        #ui {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; }}
        #judgment {{ font-size: 28px; font-weight: bold; height: 35px; margin-top: 5px; text-transform: uppercase; }}
    </style>
</head>
<body>
    <div id="ui">Score: <span id="score">0</span> | Combo: <span id="combo">0</span></div>
    <canvas id="gameCanvas" width="700" height="400"></canvas>
    <div id="judgment" style="color: #2ed573;">READY</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const rotationSpeed = {theme['speed']};
        const hitTolerance = {theme['tolerance']};
        const radius = 60; 

        let score = 0;
        let combo = 0;
        let currentTileIndex = 0;
        let isFirePivot = true; 
        let planetAngle = 0;
        
        let camera = {{ x: 0, y: 0 }};
        let flashAlpha = 0; 
        
        let tiles = [{{ x: 0, y: 0 }}];
        let currentDir = 0; 

        // 꼬이지 않는 맵 생성 알고리즘
        function addTile() {{
            let last = tiles[tiles.length - 1];
            let nextDir = currentDir;

            if (currentDir === 0)
