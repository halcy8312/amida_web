document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('amida-canvas');
    const ctx = canvas.getContext('2d');
    const startStopBtn = document.getElementById('start-stop-btn');
    const speedSlider = document.getElementById('speed-slider');

    let isRunning = false;
    let speed = 1;
    let markers = [];
    let lines = [];
    let traps = [];
    let powerups = [];
    let scores = [0, 0, 0, 0, 0];
    let markerColors = ['red', 'green', 'blue', 'yellow', 'purple'];
    let powerupTypes = ['speed', 'invincible', 'double_score'];
    let powerupEffects = [null, null, null, null, null];
    let powerupTimers = [0, 0, 0, 0, 0];
    let markerTrails = [[], [], [], [], []];

    function initialize() {
        generateLines();
        initializeMarkers();
        generateTraps();
        generatePowerups();
        draw();
    }

    function generateLines() {
        lines = [];
        let yPositions = [];
        for (let i = 0; i < 20; i++) {
            let xStart = 30 + Math.floor(Math.random() * 9) * 30;
            let xEnd = xStart + 30;
            let y = 10 + Math.floor(Math.random() * 20) * 30;
            if (!yPositions.includes(y)) {
                yPositions.push(y);
                lines.push({ xStart, xEnd, y });
            }
        }
    }

    function initializeMarkers() {
        markers = [];
        for (let i = 0; i < 5; i++) {
            let x = 30 + Math.floor(Math.random() * 10) * 30;
            let y = 10;
            markers.push({ x, y, color: markerColors[i], speed: speed, score: 0 });
        }
    }

    function generateTraps() {
        traps = [];
        for (let i = 0; i < 5; i++) {
            let x = 30 + Math.floor(Math.random() * 10) * 30;
            let y = 10 + Math.floor(Math.random() * 20) * 30;
            traps.push({ x, y });
        }
    }

    function generatePowerups() {
        powerups = [];
        for (let i = 0; i < 3; i++) {
            let x = 30 + Math.floor(Math.random() * 10) * 30;
            let y = 10 + Math.floor(Math.random() * 20) * 30;
            let type = powerupTypes[Math.floor(Math.random() * powerupTypes.length)];
            powerups.push({ x, y, type });
        }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // Draw vertical lines
        for (let i = 0; i < 10; i++) {
            let x = 30 + i * 30;
            ctx.beginPath();
            ctx.moveTo(x, 10);
            ctx.lineTo(x, 590);
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 2;
            ctx.stroke();
        }
        // Draw horizontal lines
        lines.forEach(line => {
            ctx.beginPath();
            ctx.moveTo(line.xStart, line.y);
            ctx.lineTo(line.xEnd, line.y);
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 2;
            ctx.stroke();
        });
        // Draw traps
        traps.forEach(trap => {
            ctx.fillStyle = 'red';
            ctx.fillRect(trap.x - 5, trap.y - 5, 10, 10);
        });
        // Draw powerups
        powerups.forEach(powerup => {
            ctx.beginPath();
            ctx.arc(powerup.x, powerup.y, 10, 0, Math.PI * 2);
            ctx.fillStyle = powerup.type === 'speed' ? 'blue' : powerup.type === 'invincible' ? 'green' : 'gold';
            ctx.fill();
        });
        // Draw markers
        markers.forEach(marker => {
            ctx.beginPath();
            ctx.arc(marker.x, marker.y, 5, 0, Math.PI * 2);
            ctx.fillStyle = marker.color;
            ctx.fill();
        });
    }

    function startGame() {
        isRunning = true;
        markers.forEach((marker, index) => {
            markerTrails[index] = [];
            moveMarker(index);
        });
    }

    function stopGame() {
        isRunning = false;
    }

    function moveMarker(index) {
        let marker = markers[index];
        let passedLine = false; // 横線通過フラグを追加

        let interval = setInterval(() => {
            if (!isRunning) {
                clearInterval(interval);
                return;
            }

            let moved = false;
            for (let line of lines) {
                if (!passedLine && Math.abs(marker.y - line.y) <= marker.speed) {
                    // 横線通過判定を修正
                    if (marker.x === line.xStart) {
                        marker.x = line.xEnd;
                    } else if (marker.x === line.xEnd) {
                        marker.x = line.xStart;
                    }
                    marker.y = line.y; // マーカーのy座標も更新
                    marker.score += powerupEffects[index] === 'double_score' ? 20 : 10;
                    passedLine = true; // 横線通過フラグを立てる
                    moved = true;
                    break;
                }
            }

            if (!moved) {
                marker.y += marker.speed;
                passedLine = false; // 次の横線に到達したらフラグを戻す
            }

            // Check for traps
            traps.forEach(trap => {
                if (Math.abs(marker.x - trap.x) <= 5 && Math.abs(marker.y - trap.y) <= 5) {
                    marker.score -= 20;
                    traps = traps.filter(t => t !== trap);
                }
            });
            // Check for powerups
            powerups.forEach((powerup, pIndex) => {
                if (Math.abs(marker.x - powerup.x) <= 10 && Math.abs(marker.y - powerup.y) <= 10) {
                    applyPowerup(index, powerup.type);
                    powerups.splice(pIndex, 1);
                }
            });
            // Draw trail
            if (markerTrails[index].length === 0 || Math.abs(markerTrails[index][markerTrails[index].length - 1].y - marker.y) >= 10) {
                markerTrails[index].push({ x: marker.x, y: marker.y });
            }
            if (markerTrails[index].length > 10) {
                markerTrails[index].shift();
            }
            draw();
        }, 1000 / 60);
    }

    function applyPowerup(index, type) {
        powerupEffects[index] = type;
        if (type === 'speed') {
            markers[index].speed *= 2;
        } else if (type === 'invincible') {
            // invincible logic
        } else if (type === 'double_score') {
            // double score logic
        }
        powerupTimers[index] = 5;
        setTimeout(() => {
            if (type === 'speed') {
                markers[index].speed /= 2;
            }
            powerupEffects[index] = null;
        }, 5000);
    }

    startStopBtn.addEventListener('click', function() {
        if (isRunning) {
            stopGame();
        } else {
            startGame();
        }
    });

    speedSlider.addEventListener('input', function() {
        speed = speedSlider.value * 5;
        markers.forEach(marker => {
            if (powerupEffects[markers.indexOf(marker)] !== 'speed') {
                marker.speed = speed;
            }
        });
    });

    initialize();
});
