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

# 동적 테마 CSS 적용 (중괄호 충돌이 없도록 일반 문자열로 처리)
custom_css = """
<style>
    .stApp { background-color: __BG__ !important; color: __TEXT__ !important; }
    [data-testid="stSidebar"] { background-color: __SIDEBAR_BG__ !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: __TEXT__ !important; }
</style>
"""
custom_css = custom_css.replace("__BG__", theme['bg'])
custom_css = custom_css.replace("__TEXT__", theme['text'])
custom_css = custom_css.replace("__SIDEBAR_BG__", theme['sidebar_bg'])

st.markdown(custom_css, unsafe_allow_html=True)

st.title("🔥 🧊 얼불춤: 하이라이트 가이드 모드")
st.write(f"현재 모드: **{difficulty}** | 초록색으로 빛나는 다음 타일을 조준하세요!")
st.info("⚠️ 게임 화면(검은 캔버스)을 **클릭**한 후 스페이스바를 누르세요!")

# f 기호를 빼서 f-string 에러를 완벽히 차단한 템플릿 문자열
game_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background-color: __BG__; color: __TEXT__; text-align: center; font-family: sans-serif; margin: 0; padding: 0; overflow: hidden; }
        canvas { background: #0a0a0a; border: 3px solid #555; display: block; margin: 0 auto; border-radius: 8px; box-shadow: 0 0 30px rgba(255,255,255,0.05); }
        #ui { font-size: 20px; font-weight: bold; margin-bottom: 10px; }
        #judgment { font-size: 28px; font-weight: bold; height: 35px; margin-top: 5px; text-transform: uppercase; }
    </style>
</head>
<body>
    <div id="ui">Score: <span id="score">0</span> | Combo: <span id="combo">0</span></div>
    <canvas id="gameCanvas" width="700" height="400"></canvas>
    <div id="judgment" style="color: #2ed573;">READY</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const rotationSpeed = __SPEED__;
        const hitTolerance = __TOLERANCE__;
        const radius = 60; 

        let score = 0;
        let combo = 0;
        let currentTileIndex = 0;
        let isFirePivot = true; 
        let planetAngle = 0;
        
        let camera = { x: 0, y: 0 };
        let flashAlpha = 0; 
        
        let tiles = [{ x: 0, y: 0 }];
        let currentDir = 0; 

        function addTile() {
            let last = tiles[tiles.length - 1];
            let nextDir = currentDir;

            if (currentDir === 0) { 
                let rand = Math.random();
                if (rand < 0.4) nextDir = 0;
                else if (rand < 0.7) nextDir = -1;
                else nextDir = 1;
            } else if (currentDir === -1) {
                nextDir = Math.random() < 0.5 ? -1 : 0;
            } else if (currentDir === 1) {
                nextDir = Math.random() < 0.5 ? 1 : 0;
            }

            currentDir = nextDir;
            let dx = currentDir === 0 ? 1 : 0;
            let dy = currentDir === 1 ? 1 : (currentDir === -1 ? -1 : 0);
            
            tiles.push({ x: last.x + dx * radius, y: last.y + dy * radius });
        }

        for(let i = 0; i < 25; i++) addTile();

        function getTargetAngle() {
            let current = tiles[currentTileIndex];
            let next = tiles[currentTileIndex + 1];
            return Math.atan2(next.y - current.y, next.x - current.x);
        }

        function update() {
            planetAngle += rotationSpeed;
            if (planetAngle > Math.PI * 2) planetAngle -= Math.PI * 2;
            
            let pivot = tiles[currentTileIndex];
            let targetCameraX = pivot.x - canvas.width * 0.3; 
            let targetCameraY = pivot.y - canvas.height * 0.5;
            camera.x += (targetCameraX - camera.x) * 0.12; 
            camera.y += (targetCameraY - camera.y) * 0.12;

            if (flashAlpha > 0) flashAlpha -= 0.05;

            draw();
            requestAnimationFrame(update);
        }

        function draw() {
            ctx.fillStyle = "#0a0a0a";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.save();
            ctx.translate(-camera.x, -camera.y);

            // 1. 타일 연결 선
            ctx.strokeStyle = "rgba(255,255,255,0.15)";
            ctx.lineWidth = 4;
            ctx.beginPath();
            for(let i = Math.max(0, currentTileIndex - 3); i < tiles.length; i++) {
                if(i === Math.max(0, currentTileIndex - 3)) ctx.moveTo(tiles[i].x, tiles[i].y);
                else ctx.lineTo(tiles[i].x, tiles[i].y);
            }
            ctx.stroke();

            // 2. 타일 그리기 및 색상 판정 구역
            for(let i = Math.max(0, currentTileIndex - 3); i < currentTileIndex + 18; i++) {
                if(!tiles[i]) continue;
                
                ctx.save();
                ctx.translate(tiles[i].x, tiles[i].y);
                ctx.rotate(Math.PI / 4); 
                
                if (i === currentTileIndex + 1) {
                    // ★ 가야 하는 타일: 네온 초록색
                    ctx.fillStyle = "#2ed573"; 
                    ctx.shadowBlur = 20;
                    ctx.shadowColor = "#2ed573";
                } else if (i === currentTileIndex) {
                    // 중심점 타일: 노란색
                    ctx.fillStyle = "#ffca28"; 
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = "#ffca28";
                } else if (i < currentTileIndex) {
                    // 지나간 타일: 어두운 회색
                    ctx.fillStyle = "#222222"; 
                    ctx.shadowBlur = 0;
                } else {
                    // 대기 타일: 투명도 있는 회색
                    ctx.fillStyle = "rgba(255, 255, 255, 0.3)"; 
                    ctx.shadowBlur = 0;
                }
                
                ctx.fillRect(-12, -12, 24, 24);
                ctx.restore();
            }

            // 3. 불과 얼음 공 그리기
            let pivot = tiles[currentTileIndex];
            let orbitX = pivot.x + Math.cos(planetAngle) * radius;
            let orbitY = pivot.y + Math.sin(planetAngle) * radius;

            let fireColor = "#ff4757"; 
            let iceColor = "#00a8ff";  

            ctx.fillStyle = isFirePivot ? fireColor : iceColor;
            ctx.beginPath(); ctx.arc(pivot.x, pivot.y, 14, 0, Math.PI * 2); ctx.fill();

            ctx.fillStyle = isFirePivot ? iceColor : fireColor;
            ctx.beginPath(); ctx.arc(orbitX, orbitY, 14, 0, Math.PI * 2); ctx.fill();
            
            ctx.strokeStyle = "rgba(255,255,255,0.1)";
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.arc(pivot.x, pivot.y, radius, 0, Math.PI * 2); ctx.stroke();
            
            ctx.restore();

            if (flashAlpha > 0) {
                ctx.fillStyle = `rgba(255, 255, 255, ${flashAlpha})`;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }
        }

        window.addEventListener("keydown", (e) => {
            if (e.code === "Space") {
                e.preventDefault();
                let targetAngle = getTargetAngle();
                
                let angle1 = planetAngle;
                let angle2 = targetAngle;
                let angleDiff = Math.abs((angle1 - angle2 + Math.PI * 3) % (Math.PI * 2) - Math.PI);

                const judgmentEl = document.getElementById("judgment");
                
                if (angleDiff < hitTolerance) {
                    judgmentEl.innerText = "PERFECT! 🔥";
                    judgmentEl.style.color = "#2ed573";
                    score += 100 + combo * 10;
                    combo++;
                    
                    flashAlpha = 0.3; 
                    
                    currentTileIndex++;
                    isFirePivot = !isFirePivot;
                    planetAngle = targetAngle + Math.PI; 
                    addTile();
                    
                } else if (angleDiff < hitTolerance * 2.2) {
                    judgmentEl.innerText = "GOOD";
                    judgmentEl.style.color = "#f39c12";
                    score += 50;
                    combo++;
                    
                    currentTileIndex++;
                    isFirePivot = !isFirePivot;
                    planetAngle = targetAngle + Math.PI;
                    addTile();
                } else {
                    judgmentEl.innerText = "MISS 🧊";
                    judgmentEl.style.color = "#e84118";
                    combo = 0;
                }

                document.getElementById("score").innerText = score;
                document.getElementById("combo").innerText = combo;
            }
        });

        update();
    </script>
</body>
</html>
"""

# 파이썬 내부에서 플레이스홀더 안전 치환
game_html = game_template.replace("__BG__", theme['bg'])
game_html = game_html.replace("__TEXT__", theme['text'])
game_html = game_html.replace("__SPEED__", str(theme['speed']))
game_html = game_html.replace("__TOLERANCE__", str(theme['tolerance']))

components.html(game_html, height=520)
