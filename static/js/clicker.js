const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;

let gameActive = false;
let activeCircles = [];
let clickedCircles = [];
let remaining = 8;
let correctClicks = 0;
let animationId = null;

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const remainingSpan = document.getElementById('remaining');
const correctSpan = document.getElementById('correct');
const startBtn = document.getElementById('startBtn');
const retryBtn = document.getElementById('retryBtn');
const messageArea = document.getElementById('messageArea');

canvas.width = CANVAS_WIDTH;
canvas.height = CANVAS_HEIGHT;

function drawCircleWithAlpha(circle, alpha) {
    ctx.beginPath();
    const centerX = circle.x + circle.size / 2;
    const centerY = circle.y + circle.size / 2;
    const radius = circle.size / 2;
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fillStyle = circle.color;
    ctx.globalAlpha = alpha;
    ctx.fill();
    ctx.globalAlpha = 1.0;
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.stroke();
}

function drawAllCircles() {
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    for (const circle of clickedCircles) {
        drawCircleWithAlpha(circle, 0.3);
    }
    
    for (const circle of activeCircles) {
        drawCircleWithAlpha(circle, 1.0);
    }
}

function updateStats() {
    remainingSpan.textContent = remaining;
    correctSpan.textContent = correctClicks;
}

async function fetchState() {
    if (!gameActive) return;
    
    try {
        const response = await fetch('/clicker/state');
        const data = await response.json();
        
        activeCircles = data.active_circles || [];
        clickedCircles = data.clicked_circles || [];
        remaining = data.remaining;
        correctClicks = data.correct;
        updateStats();
        drawAllCircles();
        
        if (remaining === 0) {
            gameActive = false;
            messageArea.textContent = `Игра окончена! Попаданий: ${correctClicks} из 8`;
            startBtn.style.display = 'block';
            retryBtn.style.display = 'none';
            if (animationId) cancelAnimationFrame(animationId);
        } else {
            setTimeout(() => {
                animationId = requestAnimationFrame(fetchState);
            }, 50);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        setTimeout(() => {
            animationId = requestAnimationFrame(fetchState);
        }, 100);
    }
}

canvas.addEventListener('click', async (e) => {
    if (!gameActive) {
        messageArea.textContent = 'Нажмите "Начать игру"!';
        return;
    }
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const clickX = Math.min(Math.max(0, (e.clientX - rect.left) * scaleX), CANVAS_WIDTH);
    const clickY = Math.min(Math.max(0, (e.clientY - rect.top) * scaleY), CANVAS_HEIGHT);
    
    try {
        const response = await fetch('/clicker/click', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ x: clickX, y: clickY })
        });
        const data = await response.json();
        
        if (data.hit) {
            messageArea.innerHTML = '<span style="color: #28a745;">✅ Попадание!</span>';
            setTimeout(() => { 
                if (gameActive) messageArea.textContent = 'Игра продолжается...'; 
            }, 500);
        } else {
            messageArea.innerHTML = '<span style="color: #dc3545;">❌ Мимо!</span>';
            setTimeout(() => { 
                if (gameActive) messageArea.textContent = 'Игра продолжается...'; 
            }, 500);
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
});

async function startGame() {
    try {
        const response = await fetch('/clicker/start', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            gameActive = true;
            activeCircles = data.circles;
            clickedCircles = [];
            remaining = data.total;
            correctClicks = 0;
            updateStats();
            drawAllCircles();
            
            startBtn.style.display = 'none';
            retryBtn.style.display = 'block';
            messageArea.textContent = 'Игра началась! Кликайте по кругам!';
            
            if (animationId) cancelAnimationFrame(animationId);
            fetchState();
        }
    } catch (error) {
        console.error('Ошибка:', error);
        messageArea.textContent = 'Ошибка запуска игры';
    }
}

function retryGame() {
    if (animationId) cancelAnimationFrame(animationId);
    startGame();
}

startBtn.addEventListener('click', startGame);
retryBtn.addEventListener('click', retryGame);