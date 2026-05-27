import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit ADoFaI - Action Mode", layout="centered")

# 난이도 세팅 (속도감 유지)
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

st.title("🔥 🧊 얼불춤: 액션 모드")
st.write(f"현재 모드: **{difficulty}** | 꼬이지 않는 트랙에서 극한의 속도감을 느껴보세요!")
st.info("⚠️ 게임 화면(검은 캔버스)을 **클릭**한 후 스페이스바를 누르세요!")

# 향상된 엔진: 직관적인 길 생성 & 화면 번쩍임 효과
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
        let isFirePivot = true; 
        let planetAngle = 0;
        
        let camera = {{ x: 0, y: 0 }};
        let flashAlpha = 0; // 타격감 플래시 효과 변수
        
        // 맵 생성 상태 변수
        // 방향: 0(오른쪽), 1(아래), -1(위) - 절대 왼쪽으로 가지 않음!
        let tiles = [{{ x: 0, y: 0 }}];
        let currentDir = 0; 

        // 꼬이지 않는 맵 생성 알고리즘
        function addTile() {{
            let last = tiles[tiles.length - 1];
            let nextDir = currentDir;

            if (currentDir === 0) {{ 
                // 직진 중이면 직진(40%), 위로(30%), 아래로(30%)
                let rand = Math.random();
                if (rand < 0.4) nextDir = 0;
                else if (rand < 0.7) nextDir = -1;
                else nextDir = 1;
            }} else if (currentDir === -1) {{
                // 위로 가던 중이면 계속 위로 가거나, 오른쪽으로 꺾음 (겹침 방지)
                nextDir = Math.random() < 0.5 ? -1 : 0;
            }} else if (currentDir === 1) {{
                // 아래로 가던 중이면 계속 아래로 가거나, 오른쪽으로 꺾음 (겹침 방지)
                nextDir = Math.random() < 0.5 ? 1 : 0;
            }}

            currentDir = nextDir;
            let dx = currentDir === 0 ? 1 : 0;
            let dy = currentDir === 1 ? 1 : (currentDir === -1 ? -1 : 0);
            
            tiles.push({{ x: last.x + dx * radius, y: last.y + dy * radius }});
        }}

        // 초기 맵 25개 깔아두기
        for(let i = 0; i < 25; i++) addTile();

        function getTargetAngle() {{
            let current = tiles[currentTileIndex];
            let next = tiles[currentTileIndex + 1];
            return Math.atan2(next.y - current.y, next.x - current.x);
        }}

        function update() {{
            planetAngle += rotationSpeed;
            if (planetAngle > Math.PI * 2) planetAngle -= Math.PI * 2;
            
            // 향상된 카메라 워킹: 캐릭터를 화면 왼쪽에 치우치게 두어 앞길을 넓게 보여줌
            let pivot = tiles[currentTileIndex];
            let targetCameraX = pivot.x - canvas.width * 0.3; 
            let targetCameraY = pivot.y - canvas.height * 0.5;
            camera.x += (targetCameraX - camera.x) * 0.12; // 반응속도 증가
            camera.y += (targetCameraY - camera.y) * 0.12;

            // 화면 플래시 감소
            if (flashAlpha > 0) flashAlpha -= 0.05;

            draw();
            requestAnimationFrame(update);
        }}

        function draw() {{
            // 배경 초기화
            ctx.fillStyle = "#0a0a0a";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.save();
            ctx.translate(-camera.x, -camera.y);

            // 1. 타일 연결 선
            ctx.strokeStyle = "rgba(255,255,255,0.25)";
            ctx.lineWidth = 5;
            ctx.beginPath();
            for(let i = Math.max(0, currentTileIndex - 3); i < tiles.length; i++) {{
                if(i === Math.max(0, currentTileIndex - 3)) ctx.moveTo(tiles[i].x, tiles[i].y);
                else ctx.lineTo(tiles[i].x, tiles[i].y);
            }}
            ctx.stroke();

            // 2. 타일 사각형 그리기 (다이아몬드 형태로 회전)
            for(let i = Math.max(0, currentTileIndex - 3); i < currentTileIndex + 18; i++) {{
                if(!tiles[i]) continue;
                
                ctx.save();
                ctx.translate(tiles[i].x, tiles[i].y);
                ctx.rotate(Math.PI / 4); // 45도 회전하여 다이아몬드 모양으로
                
                if (i === currentTileIndex) {{
                    ctx.fillStyle = "#ffca28"; // 현재 타일
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = "#ffca28";
                }} else if (i < currentTileIndex) {{
                    ctx.fillStyle = "#333"; // 지나온 타일
                    ctx.shadowBlur = 0;
                }} else {{
                    ctx.fillStyle = "#bdc3c7"; // 앞으로 갈 타일
                    ctx.shadowBlur = 0;
                }}
                
                ctx.fillRect(-12, -12, 24, 24);
                ctx.restore();
            }}

            // 3. 투핑거 공 그리기
            let pivot = tiles[currentTileIndex];
            let orbitX = pivot.x + Math.cos(planetAngle) * radius;
            let orbitY = pivot.y + Math.sin(planetAngle) * radius;

            let fireColor = "#ff4757"; 
            let iceColor = "#00a8ff";  

            // 중심 공
            ctx.fillStyle = isFirePivot ? fireColor : iceColor;
            ctx.beginPath(); ctx.arc(pivot.x, pivot.y, 14, 0, Math.PI * 2); ctx.fill();

            // 회전 공
            ctx.fillStyle = isFirePivot ? iceColor : fireColor;
            ctx.beginPath(); ctx.arc(orbitX, orbitY, 14, 0, Math.PI * 2); ctx.fill();
            
            // 궤도 가이드라인
            ctx.strokeStyle = "rgba(255,255,255,0.15)";
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.arc(pivot.x, pivot.y, radius, 0, Math.PI * 2); ctx.stroke();
            
            ctx.restore();

            // 4. 플래시 이펙트 (화면 전체 덮기)
            if (flashAlpha > 0) {{
                ctx.fillStyle = `rgba(255, 255, 255, ${{flashAlpha}})`;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }}
        }}

        window.addEventListener("keydown", (e) => {{
            if (e.code === "Space") {{
                e.preventDefault();
                let targetAngle = getTargetAngle();
                
                let angle1 = planetAngle;
                let angle2 = targetAngle;
                let angleDiff = Math.abs((angle1 - angle2 + Math.PI * 3) % (Math.PI * 2) - Math.PI);

                const judgmentEl = document.getElementById("judgment");
                
                if (angleDiff < hitTolerance) {{
                    judgmentEl.innerText = "PERFECT! 🔥";
                    judgmentEl.style.color = "#4cd137";
                    score += 100 + combo * 10;
                    combo++;
                    
                    flashAlpha = 0.4; // 화면 번쩍임 효과 발동!
                    
                    currentTileIndex++;
                    isFirePivot = !isFirePivot;
                    planetAngle = targetAngle + Math.PI; 
                    addTile();
                    
                }} else if (angleDiff < hitTolerance * 2.2) {{
                    judgmentEl.innerText = "GOOD";
                    judgmentEl.style.color = "#f39c12";
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
