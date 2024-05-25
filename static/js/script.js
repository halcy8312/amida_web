document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('amida-container');
    const startStopBtn = document.getElementById('start-stop-btn');
    const speedSlider = document.getElementById('speed-slider');

    let isRunning = false;
    let speed = 2;
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
        container.innerHTML = '';
        // Draw vertical lines
        for (let i = 0; i < 10; i++) {
            let x = 30 + i * 30;
            let line = document.createElement('div');
            line.style.position = 'absolute';
            line.style.left = `${x}px`;
            line.style.top = '10px';
            line.style.width = '2px';
            line.style.height = '580px';
            line.style.backgroundColor = 'white';
            container.appendChild(line);
        }
        // Draw horizontal lines
        lines.forEach(line => {
            let path = document.createElement('div');
            path.style.position = 'absolute';
            path.style.left = `${line.xStart}px`;
            path.style.top = `${line.y}px`;
            path.style.width = `${line.xEnd - line.xStart}px`;
            path.style.height = '2px';
            path.style.backgroundColor = 'white';
            container.appendChild(path);
        });
        // Draw traps
        traps.forEach(trap => {
            let trapDiv = document.createElement('div');
            trapDiv.style.position = 'absolute';
            trapDiv.style.left = `${trap.x - 5}px`;
            trapDiv.style.top = `${trap.y - 5}px`;
            trapDiv.style.width = '10px';
            trapDiv.style.height = '10px';
            trapDiv.style.backgroundColor = 'red';
            container.appendChild(trapDiv);
        });
        // Draw powerups
        powerups.forEach(powerup => {
            let powerupDiv = document.createElement('div');
            powerupDiv.style.position = 'absolute';
            powerupDiv.style.left = `${powerup.x - 10}px`;
            powerupDiv.style.top = `${powerup.y - 10}px`;
            powerupDiv.style.width = '20px';
            powerupDiv.style.height = '20px';
            powerupDiv.style.borderRadius = '50%';
            powerupDiv.style.backgroundColor = powerup.type === 'speed' ? 'blue' :
                powerup.type === 'invincible' ? 'green' : 'gold';
            container.appendChild(powerupDiv);
        });
        // Draw markers
        markers.forEach(marker => {
            let markerDiv = document.createElement('div');
            markerDiv.style.position = 'absolute';
            markerDiv.style.left = `${marker.x - 5}px`;
            markerDiv.style.top = `${marker.y - 5}px`;
            markerDiv.style.width = '10px';
            markerDiv.style.height = '10px';
            markerDiv.style.borderRadius = '50%';
            markerDiv.style.backgroundColor = marker.color;
            container.appendChild(markerDiv);
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
        let interval = setInterval(() => {
            if (!isRunning) {
                clearInterval(interval);
                return;
            }
            // Move logic
            let moved = false;
            for (let line of lines) {
                if (marker.y === line.y && (marker.x === line.xStart || marker.x === line.xEnd)) {
                    if (marker.x === line.xStart) {
                        marker.x = line.xEnd;
                    } else {
                        marker.x = line.xStart;
                    }
                    marker.score += powerupEffects[index] === 'double_score' ? 20 : 10;
                    moved = true;
                    break;
                }
            }
            if (!moved) {
                marker.y += marker.speed;
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
        speed = speedSlider.value;
        markers.forEach(marker => {
            if (powerupEffects[markers.indexOf(marker)] !== 'speed') {
                marker.speed = speed;
            }
        });
    });

    initialize();
});
