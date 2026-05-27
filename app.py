import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit ADoFaI", layout="centered")

# 1. 난이도 및 스피드 대폭 상향
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
        "speed": 0.13, "tolerance": 0.12 # 굉장히 빠르고 판정이 빡빡함
    }
}

st.sidebar.header("🕹️ 게임 설정")
difficulty = st.sidebar.selectbox("난이도 선택", ["Easy", "Normal", "Hard"])
theme = themes[difficulty]

# 동적 테마 적용
custom_css = f"""
<style>
    .stApp {{ background-color: {theme['bg']} !important; color: {theme['text']} !important; }}
    [data-testid="stSidebar"] {{ background-color: {theme['sidebar_bg']} !important; }}
    h1, h2, h3, p, span, label, .stMarkdown {{ color: {theme['text']} !important; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.title("🔥 🧊 무한 얼불춤 (Infinity Mode)")
st.write(f"현재 모드: **{difficulty}** | 무한히 생성되는 트랙을 달려보세요!")
st.info("⚠️ 게임 화면(검은 캔버스)을 **클릭**한 후 스페이스바를 누르세요!")

# 2. 강력해진 HTML5 + JS 엔진 (투 핑거, 카메라 추적, 무한 맵)
game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background-color: {theme['bg']}; color: {theme['text']}; text-align: center; font-family: sans-serif; margin: 0; padding: 0; overflow: hidden; }}
        canvas {{ background: #0a0a0a; border: 3px solid #555; display: block; margin: 0 auto; border-radius: 8px; box-shadow: 0 0 20px rgba(255,255,255,0.1); }}
        #ui {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; }}
        #judgment {{ font-size: 28px; font-weight: bold; height: 35px; margin-top: 5px; }}
    </style>
</head>
<body>
    <div id="ui">Score: <span id="score">0</span> | Combo: <span id="combo">0</span></div>
    <canvas id="gameCanvas" width="700" height="400"></canvas>
    <div id="judgment" style="color: #4cd137;">READY</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const rotationSpeed = {theme['speed']};
        const hitTolerance = {theme['tolerance']};
        const radius = 60; // 타일 간격 및 회전 반경

        let score = 0;
        let combo = 0;
        let currentTileIndex = 0;
        let isFirePivot = true; // 불과 얼음 교대 변수
        let planetAngle = 0;
        
        // 카메라 (화면 이동)
        let camera = {{ x: 0, y: 0 }};
        
        // 무한 맵 생성기
        let tiles = [{{ x: 0, y: 0 }}];
        let currentDir = 0; // 0:우, 1:하, 2:좌, 3:상

        function addTile() {{
            let last = tiles[tiles.length - 1];
            // 70% 확률로 직진, 30% 확률로 90도 꺾임
            if (Math.random() < 0.3) {{
                currentDir = (currentDir + (Math.random() < 0.5 ? 1 : -1) + 4) % 4;
            }}
            let dx = currentDir === 0 ? 1 : currentDir === 2 ? -1 : 0;
            let dy = currentDir === 1 ? 1 : currentDir === 3 ? -1 : 0;
            tiles.push({{ x: last.x + dx * radius, y: last.y + dy * radius }});
        }}

        // 초기 맵 20개 깔아두기
        for(let i = 0; i < 20; i++) addTile();

        function getTargetAngle() {{
            let current = tiles[currentTileIndex];
            let next = tiles[currentTileIndex + 1];
            return Math.atan2(next.y - current.y, next.x - current.x);
        }}

        // 게임 루프
        function update() {{
            planetAngle += rotationSpeed;
            if (planetAngle > Math.PI * 2) planetAngle -= Math.PI * 2;
            
            // 카메라가 현재 중심점을 부드럽게 따라가도록 설정 (Smooth Damp)
            let pivot = tiles[currentTileIndex];
            let targetCameraX = pivot.x - canvas.width / 2;
            let targetCameraY = pivot.y - canvas.height / 2;
            camera.x += (targetCameraX - camera.x) * 0.1;
            camera.y += (targetCameraY - camera.y) * 0.1;

            draw();
            requestAnimationFrame(update);
        }}

        // 그리기 함수
        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.save();
            // 카메라 시점 적용
            ctx.translate(-camera.x, -camera.y);

            // 1. 타일 및 경로 선 그리기
            ctx.strokeStyle = "rgba(255,255,255,0.2)";
            ctx.lineWidth = 4;
            ctx.beginPath();
            for(let i = Math.max(0, currentTileIndex - 5); i < tiles.length; i++) {{
                if(i === Math.max(0, currentTileIndex - 5)) ctx.moveTo(tiles[i].x, tiles[i].y);
                else ctx.lineTo(tiles[i].x, tiles[i].y);
            }}
            ctx.stroke();

            // 타일 사각형 그리기
            for(let i = Math.max(0, currentTileIndex - 5); i < currentTileIndex + 15; i++) {{
                if(!tiles[i]) continue;
                ctx.fillStyle = i === currentTileIndex ? "#ffca28" : (i < currentTileIndex ? "#333" : "#bdc3c7");
                ctx.fillRect(tiles[i].x - 15, tiles[i].y - 15, 30, 30);
            }}

            // 2. 투핑거 공 그리기 (불과 얼음)
            let pivot = tiles[currentTileIndex];
            let orbitX = pivot.x + Math.cos(planetAngle) * radius;
            let orbitY = pivot.y + Math.sin(planetAngle) * radius;

            let fireColor = "#ff4757"; // 빨강
            let iceColor = "#00a8ff";  // 파랑

            // 중심점 공 그리기
            ctx.fillStyle = isFirePivot ? fireColor : iceColor;
            ctx.beginPath(); ctx.arc(pivot.x, pivot.y, 12, 0, Math.PI * 2); ctx.fill();

            // 회전하는 공 그리기
            ctx.fillStyle = isFirePivot ? iceColor : fireColor;
            ctx.beginPath(); ctx.arc(orbitX, orbitY, 12, 0, Math.PI * 2); ctx.fill();
            
            // 궤도 가이드
            ctx.strokeStyle = "rgba(255,255,255,0.1)";
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.arc(pivot.x, pivot.y, radius, 0, Math.PI * 2); ctx.stroke();

            ctx.restore();
        }}

        // 조작 및 판정
        window.addEventListener("keydown", (e) => {{
            if (e.code === "Space") {{
                e.preventDefault();

                let targetAngle = getTargetAngle();
                
                // 각도 오차 계산 (얼불춤 핵심 판정)
                let angle1 = planetAngle;
                let angle2 = targetAngle;
                let angleDiff = Math.abs((angle1 - angle2 + Math.PI * 3) % (Math.PI * 2) - Math.PI);

                const judgmentEl = document.getElementById("judgment");
                
                if (angleDiff < hitTolerance) {{
                    judgmentEl.innerText = "PERFECT! 🔥";
                    judgmentEl.style.color = "#4cd137";
                    score += 100 + combo * 10;
                    combo++;
                    
                    // 핵심 메커니즘: 중심점 이동 및 공 역할 체인지!
                    currentTileIndex++;
                    isFirePivot = !isFirePivot;
                    // 다음 궤도를 위해 회전 중이던 공의 각도를 반전시킴
                    planetAngle = targetAngle + Math.PI; 
                    
                    // 무한 맵 생성
                    addTile();
                    
                }} else if (angleDiff < hitTolerance * 2.0) {{
                    judgmentEl.innerText = "EARLY / LATE";
                    judgmentEl.style.color = "#e1b12c";
                    score += 50;
                    combo++;
                    
                    currentTileIndex++;
                    isFirePivot = !isFirePivot;
                    planetAngle = targetAngle + Math.PI;
                    addTile();
                }} else {{
                    judgmentEl.innerText = "MISS 🧊";
                    judgmentEl.style.color = "#e84118";
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

components.html(game_html, height=520)
