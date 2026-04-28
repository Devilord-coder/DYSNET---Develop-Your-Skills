let cards = [];
let moves = 0;
let foundPairs = 0;
let currentGridSize = 4;
let waiting = false;
let stateTimeout = null;

const board = document.getElementById('memoryBoard');
const movesSpan = document.getElementById('moves');
const foundSpan = document.getElementById('found');
const gridSizeSelect = document.getElementById('gridSize');
const newGameBtn = document.getElementById('newGameBtn');

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    startNewGame();
});

function setupEventListeners() {
    gridSizeSelect.addEventListener('change', () => {
        currentGridSize = parseInt(gridSizeSelect.value);
        startNewGame();
    });
    newGameBtn.addEventListener('click', () => {
        startNewGame();
    });
}

async function startNewGame() {
    if (stateTimeout) clearTimeout(stateTimeout);
    waiting = false;
    
    try {
        const response = await fetch('/memory/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ size: currentGridSize })
        });
        const data = await response.json();
        
        cards = data.cards;
        moves = data.moves;
        foundPairs = data.found_pairs;
        
        updateStats();
        renderBoard();
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

function updateStats() {
    movesSpan.textContent = moves;
    foundSpan.textContent = foundPairs;
}

function renderBoard() {
    board.innerHTML = '';
    board.setAttribute('data-size', currentGridSize);
    
    cards.forEach((card) => {
        const cardElement = createCardElement(card);
        board.appendChild(cardElement);
    });
}

function createCardElement(card) {
    const div = document.createElement('div');
    div.className = 'card';
    if (card.flipped) div.classList.add('flipped');
    if (card.matched) div.classList.add('matched');
    
    const content = document.createElement('div');
    content.className = 'card-content';
    
    if (card.flipped || card.matched) {
        if (card.image && card.image !== null) {
            const img = document.createElement('img');
            img.src = card.image;
            img.style.width = '80%';
            img.style.height = '80%';
            img.style.objectFit = 'contain';
            content.appendChild(img);
        } else {
            content.textContent = card.emoji;
            content.style.fontSize = '2.5rem';
        }
    } else {
        content.textContent = '?';
        content.style.fontSize = '2.5rem';
        content.style.fontWeight = 'bold';
        content.style.color = 'white';
    }
    
    div.appendChild(content);
    div.addEventListener('click', () => onCardClick(card.card_id));
    
    return div;
}

async function onCardClick(cardId) {
    if (waiting) return;
    
    try {
        const response = await fetch('/memory/flip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ card_id: cardId })
        });
        const data = await response.json();
        
        cards = data.cards;
        moves = data.moves;
        foundPairs = data.found_pairs;
        waiting = data.waiting;
        
        updateStats();
        renderBoard();
        
        if (waiting) {
            if (stateTimeout) clearTimeout(stateTimeout);
            stateTimeout = setTimeout(async () => {
                const stateResponse = await fetch('/memory/state');
                const stateData = await stateResponse.json();
                
                cards = stateData.cards;
                moves = stateData.moves;
                foundPairs = stateData.found_pairs;
                waiting = false;
                
                updateStats();
                renderBoard();
                stateTimeout = null;
            }, 1000);
        }
        
        if (foundPairs === cards.length / 2) {
            if (stateTimeout) clearTimeout(stateTimeout);
            setTimeout(() => {
                alert(`Поздравляем! Вы выиграли за ${moves} ходов!`);
            }, 100);
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}