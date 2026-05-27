import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="Streamlit Mini Fire & Ice", layout="centered")

# 1. 난이도별 테마 색상 정의 (조화롭고 눈이 편안한 다크 모드 기반 스타일)
themes = {
    "Easy": {
        "bg": "#050806",          # 아주 깊은 검은색에 가까운 초록
        "sidebar_bg": "#0D140F",   # 톤다운된 딥 포레스트 그린
        "text": "#E0F2F1",        # 부드러운 민트 화이트
        "primary": "#00E676",     # 네온 형광 초록 (현재 타일 & 판정)
        "secondary": "#1B5E20",   # 짙은 초록 (대기 타일)
        "passed": "#37474F",      # 지나온 타일 (차분한 회색)
        "speed": 0.03,
        "tolerance": 0.25
    },
    "Normal": {
        "bg": "#141008",       # 깊고 따뜻한 다크 브라운
        "sidebar_bg": "#1F180D",# 묵직한 주황빛 도는 다크 그레이
        "text": "#FFF8E1",     # 따뜻한 크림 화이트
        "primary": "#FFB300",  # 선명한 황금빛 노란색
        "secondary": "#E65100",# 타오르는 주황색
        "passed": "#4E342E",   # 지나온 타일 (차분한 갈색)
        "speed": 0.06,
        "tolerance": 0.15
    },
    "Hard": {
        "bg": "#050B14",       # 심해 느낌의 깊은 사이버 네이비
        "sidebar_bg": "#0A1424",# 미드나잇 블루
        "text": "#E3F2FD",     # 시원한 아이스 화이트
        "primary": "#00E5FF",  # 청량한 하늘색/사이언
        "secondary": "#0D47A1",# 정통 파란색
        "passed": "#263238",   # 지나온 타일 (차분한 네이비 그레이)
        "speed": 0.09,
        "tolerance": 0.07
    }
}

# 사이드바에서 난이도 선택
st.sidebar.header("🕹️ 게임 설정")
difficulty = st.sidebar.selectbox("난이도 선택", ["Easy", "Normal", "Hard"])

# 현재 선택된 테마 데이터 가져오기
theme = themes[difficulty]

# 2. Streamlit 전체 화면에 동적 CSS 주입
# (선택한 난이도에 따라 배경색과 텍스트 색상이 실시간으로 변경됩니다)
custom_css = f"""
<style>
    /* 메인 화면 배경 및 글자색 */
    .stApp {{
        background-color: {theme['bg']} !important;
        color: {theme['text']} !important;
    }}
    /* 사이드바 배경 및 글자색 */
    [data-testid="stSidebar"] {{
        background-color: {theme['sidebar_bg']} !important;
    }}
    /* 모든 타이틀 및 텍스트 색상 강제 지정 */
    h1, h2, h3, p, span, label, .stMarkdown {{
        color: {theme['text']} !important;
    }}
    /* 안내창(st.info) 스타일 살짝 매칭 */
    .stAlert {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid {theme['primary']} !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 메인 UI 구성
st.title("🔥 🧊 미니 얼불춤")
st.write(f"현재 모드: **{difficulty}** (회전 속도: {theme['speed']} | 판정 범위: {theme['tolerance']})")

st.info("⚠️ **시작 전 필수:** 게임 화면(캔버스)을 마우스로 **한 번 클릭**한 뒤 스페이스바를 누르세요!")

# 3. HTML5 Canvas + JavaScript 게임 엔진 (테마 색상 연동)
game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background-color: {theme['bg']}; color: {theme['text']}; text-align: center; font-family: sans-serif; margin: 0; padding: 0; }}
        canvas {{ background: #000000; border: 3px solid {theme['primary']}; display: block; margin: 10px auto; border-radius: 8px; box-shadow: 0 0 15px {theme['primary']}40; }}
        #ui {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; color: {theme['text']}; }}
        #judgment {{ font-size: 26px; font-weight: bold; height: 35px; color: {theme['primary']}; margin-top: 5px; text-shadow: 0 0 8px {theme['primary']}; }}
    </style>
</head>
<body>
    <div id="ui">Score: <span id="score">0</span> | Combo: <span id="combo">0</span></div>
    <canvas id="gameCanvas" width="700" height="350"></canvas>
    <div id="judgment">READY</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Python 테마에서 받아온 동적 변수들
        const rotationSpeed = {theme['speed']};
        const hitTolerance = {theme['tolerance']};
        const colorPrimary = "{theme['primary']}";
        const colorSecondary = "{theme['secondary']}";
        const colorPassed = "{theme['passed']}";

        let pivot = {{ x: 150, y: 175 }};
        let planetAngle = 0;
        let score = 0;
        let combo = 0;
        
        let tiles = [
            {{ x: 150, y: 175 }}, {{ x: 270, y: 175 }}, {{ x: 390, y: 175 }},
            {{ x: 390, y: 270 }}, {{ x: 510, y: 270 }}, {{ x: 510, y: 120 }},
            {{ x: 630, y: 120 }}
        ];
        let currentTileIndex = 0;
        const radius = 60;

        function getTargetAngle() {{
            if (currentTileIndex >= tiles.length - 1) return 0;
            let current = tiles[currentTileIndex];
            let next = tiles[currentTileIndex + 1];
            return Math.atan2(next.y - current.y, next.x - current.x);
        }}

        function update() {{
            planetAngle += rotationSpeed;
            if (planetAngle > Math.PI * 2) planetAngle -= Math.PI * 2;
            draw();
            requestAnimationFrame(update);
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. 타일 그리기 (테마 색상 적용)
            tiles.forEach((tile, index) => {{
                if (index === currentTileIndex) ctx.fillStyle = colorPrimary; // 현재 타일
                else if (index < currentTileIndex) ctx.fillStyle = colorPassed; // 지나온 타일
                else ctx.fillStyle = colorSecondary; // 대기 타일
                
                ctx.beginPath();
                ctx.arc(tile.x, tile.y, 14, 0, Math.PI * 2);
                ctx.fill();
                
                // 현재 타일에 빛나는 효과(Glow)
                if(index === currentTileIndex) {{
                    ctx.strokeStyle = "rgba(255,255,255,0.5)";
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }}
            }});

            if (currentTileIndex >= tiles.length - 1) {{
                ctx.fillStyle = colorPrimary;
                ctx.font = "bold 32px sans-serif";
                ctx.fillText("🎉 STAGE CLEAR! 🎉", canvas.width/2 - 150, canvas.height/2);
                return;
            }}

            // 2. 회전하는 행성 그리기
            let planetX = pivot.x + Math.cos(planetAngle) * radius;
            let planetY = pivot.y + Math.sin(planetAngle) * radius;

            ctx.fillStyle = "#FFFFFF"; // 행성은 깔끔하게 흰색으로 통일하여 가시성 확보
            ctx.beginPath();
            ctx.arc(planetX, planetY, 10, 0, Math.PI * 2);
            ctx.fill();

            // 궤도 점선
            ctx.strokeStyle = "rgba(255,255,255,0.12)";
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(pivot.x, pivot.y, radius, 0, Math.PI * 2);
            ctx.stroke();
        }}

        window.addEventListener("keydown", (e) => {{
            if (e.code === "Space") {{
                e.preventDefault();
                if (currentTileIndex >= tiles.length - 1) return;

                let targetAngle = getTargetAngle();
                let angleDiff = Math.abs(planetAngle - targetAngle);
                angleDiff = Math.min(angleDiff, Math.PI * 2 - angleDiff);

                const judgmentEl = document.getElementById("judgment");
                
                if (angleDiff < hitTolerance) {{
                    judgmentEl.innerText = "PERFECT! 🔥";
                    judgmentEl.style.color = colorPrimary;
                    score += 100 + combo * 10;
                    combo++;
                    currentTileIndex++;
                    pivot = tiles[currentTileIndex];
                }} else if (angleDiff < hitTolerance * 1.8) {{
                    judgmentEl.innerText = "GOOD 👍";
                    judgmentEl.style.color = "#FFFFFF";
                    score += 50;
                    combo++;
                    currentTileIndex++;
                    pivot = tiles[currentTileIndex];
                }} else {{
                    judgmentEl.innerText = "MISS 🧊";
                    judgmentEl.style.color = "#FF4757";
                    combo = 0;
                }}

                document.getElementById("score").innerText = score;
                document.getElementById("combo").innerText = combo;
            }}
        }});

        update();
    </script>
</body>
</html>
"""

components.html(game_html, height=460)
