import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="Streamlit Mini Fire & Ice", layout="centered")

st.title("🔥 🧊 미니 얼불춤 (Streamlit 버전)")
st.write("사이드바에서 난이도를 조절하고 대시보드에서 실시간 리듬 게임을 즐겨보세요.")

# 1. Streamlit 사이드바 UI - 난이도 조절
st.sidebar.header("🕹️ 게임 설정")
difficulty = st.sidebar.selectbox("난이도 선택", ["Easy", "Normal", "Hard"])

# 난이도별 데이터 세팅 (파이썬에서 자바스크립트로 주입할 값)
if difficulty == "Easy":
    speed = 0.03        # 공이 회전하는 속도
    tolerance = 0.25    # 판정 범위 (라디안 단위, 클수록 널널함)
elif difficulty == "Normal":
    speed = 0.06
    tolerance = 0.15
else:  # Hard
    speed = 0.09
    tolerance = 0.07

st.sidebar.markdown(f"""
---
* **현재 난이도:** `{difficulty}`
* **회전 속도 (BPM):** `{speed}`
* **판정 범위:** `{tolerance}` (낮을수록 칼타이밍 요구)
""")

# 플레이 가이드 경고창
st.info("⚠️ **중요:** 게임을 시작하기 전에 반드시 **게임 화면(검은색 캔버스)을 마우스로 한 번 클릭**해 주세요! 그래야 스페이스바 입력이 게임으로 전달됩니다.")

# 2. HTML5 Canvas + JavaScript 게임 엔진 코드
# (Python의 f-string을 사용하므로, JS의 중괄호 {}는 {{}}로 이중 처리해야 합니다)
game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background-color: #0e1117; color: white; text-align: center; font-family: sans-serif; margin: 0; padding: 0; }}
        canvas {{ background: #111; border: 3px solid #444; display: block; margin: 10px auto; border-radius: 8px; }}
        #ui {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #fafafa; }}
        #judgment {{ font-size: 26px; font-weight: bold; height: 35px; color: #ffca28; margin-top: 5px; }}
    </style>
</head>
<body>
    <div id="ui">Score: <span id="score">0</span> | Combo: <span id="combo">0</span></div>
    <canvas id="gameCanvas" width="700" height="350"></canvas>
    <div id="judgment">게임을 클릭하고 스페이스바를 누르세요!</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Python에서 동적으로 넘겨받은 난이도 변수 설정
        const rotationSpeed = {speed};
        const hitTolerance = {tolerance};

        let pivot = {{ x: 150, y: 175 }};
        let planetAngle = 0;
        let score = 0;
        let combo = 0;
        
        // 지그재그 및 꺾이는 타일 맵 데이터 (좌표값)
        let tiles = [
            {{ x: 150, y: 175 }},
            {{ x: 270, y: 175 }},
            {{ x: 390, y: 175 }},
            {{ x: 390, y: 270 }},
            {{ x: 510, y: 270 }},
            {{ x: 510, y: 120 }},
            {{ x: 630, y: 120 }}
        ];
        let currentTileIndex = 0;
        const radius = 60; // 회전 반경

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

            // 1. 타일선 및 타일 그리기
            tiles.forEach((tile, index) => {{
                if (index === currentTileIndex) ctx.fillStyle = "#ff4757"; // 현재 목표 타일 (빨강)
                else if (index < currentTileIndex) ctx.fillStyle = "#57606f"; // 지나온 타일 (회색)
                else ctx.fillStyle = "#2e86de"; // 앞으로 갈 타일 (파랑)
                
                ctx.beginPath();
                ctx.arc(tile.x, tile.y, 14, 0, Math.PI * 2);
                ctx.fill();
            }});

            // 클리어 조건 체크
            if (currentTileIndex >= tiles.length - 1) {{
                ctx.fillStyle = "#2ed573";
                ctx.font = "bold 32px sans-serif";
                ctx.fillText("🎉 STAGE CLEAR! 🎉", canvas.width/2 - 150, canvas.height/2);
                return;
            }}

            // 2. 회전하는 행성(공) 위치 계산 및 그리기
            let planetX = pivot.x + Math.cos(planetAngle) * radius;
            let planetY = pivot.y + Math.sin(planetAngle) * radius;

            ctx.fillStyle = "#ffa502"; // 주황색 공
            ctx.beginPath();
            ctx.arc(planetX, planetY, 10, 0, Math.PI * 2);
            ctx.fill();

            // 가이드 점선 궤도
            ctx.strokeStyle = "rgba(255,255,255,0.15)";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(pivot.x, pivot.y, radius, 0, Math.PI * 2);
            ctx.stroke();
        }}

        // 키보드 판정 이벤트
        window.addEventListener("keydown", (e) => {{
            if (e.code === "Space") {{
                e.preventDefault(); // 스페이스바 누를 때 웹페이지 스크롤 방지
                if (currentTileIndex >= tiles.length - 1) return;

                let targetAngle = getTargetAngle();
                let angleDiff = Math.abs(planetAngle - targetAngle);
                angleDiff = Math.min(angleDiff, Math.PI * 2 - angleDiff); // 최소 각도 구하기

                const judgmentEl = document.getElementById("judgment");
                
                if (angleDiff < hitTolerance) {{
                    judgmentEl.innerText = "PERFECT! 🔥";
                    judgmentEl.style.color = "#2ed573";
                    score += 100 + combo * 10;
                    combo++;
                    currentTileIndex++;
                    pivot = tiles[currentTileIndex]; // 중심점 이동!
                }} else if (angleDiff < hitTolerance * 1.8) {{
                    judgmentEl.innerText = "GOOD 👍";
                    judgmentEl.style.color = "#eccc68";
                    score += 50;
                    combo++;
                    currentTileIndex++;
                    pivot = tiles[currentTileIndex];
                }} else {{
                    judgmentEl.innerText = "MISS 🧊";
                    judgmentEl.style.color = "#ff4757";
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

# Streamlit에 하이브리드 게임 컴포넌트 장착
components.html(game_html, height=460)
