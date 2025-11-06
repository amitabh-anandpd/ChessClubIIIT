// Chess Match JavaScript - Interactive Chessboard

class ChessMatch {
  constructor() {
    this.game = new Chess();
    this.selectedSquare = null;
    this.isFlipped = false;
    this.moveHistory = [];
    
    this.init();
  }

  init() {
    this.createBoard();
    this.updateDisplay();
    this.setupEventListeners();
    console.log('Chess match initialized');
  }

  createBoard() {
    const board = document.getElementById('chessboard');
    board.innerHTML = '';

    for (let rank = 8; rank >= 1; rank--) {
      for (let file = 0; file < 8; file++) {
        const square = document.createElement('div');
        const fileChar = String.fromCharCode(97 + file); // a-h
        const squareName = fileChar + rank;
        
        square.className = `square ${(rank + file) % 2 === 0 ? 'dark' : 'light'}`;
        square.dataset.square = squareName;
        square.addEventListener('click', (e) => this.handleSquareClick(e));
        
        board.appendChild(square);
      }
    }
  }

  updateDisplay() {
    this.updateBoard();
    this.updateGameStatus();
    this.updateMoveHistory();
    this.updateGameInfo();
  }

  updateBoard() {
    const squares = document.querySelectorAll('.square');
    
    squares.forEach(square => {
      const squareName = square.dataset.square;
      const piece = this.game.get(squareName);
      
      // Clear previous piece
      square.innerHTML = '';
      square.classList.remove('has-piece', 'selected', 'legal-move', 'last-move', 'in-check');
      
      // Add piece if present
      if (piece) {
        const pieceElement = document.createElement('div');
        const colorClass = piece.color === 'w' ? 'white' : 'black';
        const typeMap = { p: 'pawn', r: 'rook', n: 'knight', b: 'bishop', q: 'queen', k: 'king' };
        const typeClass = typeMap[piece.type];
        pieceElement.className = `piece ${colorClass} ${typeClass}`;
        square.appendChild(pieceElement);
        square.classList.add('has-piece');
      }
      
      // Highlight selected square
      if (this.selectedSquare === squareName) {
        square.classList.add('selected');
      }
      
      // Highlight legal moves
      if (this.selectedSquare) {
        const moves = this.game.moves({ square: this.selectedSquare, verbose: true });
        if (moves.some(move => move.to === squareName)) {
          square.classList.add('legal-move');
        }
      }
      
      // Highlight last move
      const history = this.game.history({ verbose: true });
      if (history.length > 0) {
        const lastMove = history[history.length - 1];
        if (squareName === lastMove.from || squareName === lastMove.to) {
          square.classList.add('last-move');
        }
      }
      
      // Highlight check
      if (this.game.in_check()) {
        const kingSquare = this.findKingSquare(this.game.turn());
        if (squareName === kingSquare) {
          square.classList.add('in-check');
        }
      }
    });
  }

  findKingSquare(color) {
    const board = this.game.board();
    for (let rank = 0; rank < 8; rank++) {
      for (let file = 0; file < 8; file++) {
        const piece = board[rank][file];
        if (piece && piece.type === 'k' && piece.color === color) {
          return String.fromCharCode(97 + file) + (8 - rank);
        }
      }
    }
    return null;
  }

  handleSquareClick(event) {
    const square = event.currentTarget;
    const squareName = square.dataset.square;
    const piece = this.game.get(squareName);
    
    // If no square is selected
    if (!this.selectedSquare) {
      if (piece && piece.color === this.game.turn()) {
        this.selectedSquare = squareName;
        this.updateDisplay();
      }
      return;
    }
    
    // If clicking the same square, deselect
    if (this.selectedSquare === squareName) {
      this.selectedSquare = null;
      this.updateDisplay();
      return;
    }
    
    // If clicking another piece of the same color, select it
    if (piece && piece.color === this.game.turn()) {
      this.selectedSquare = squareName;
      this.updateDisplay();
      return;
    }
    
    // Try to make a move
    this.attemptMove(this.selectedSquare, squareName);
  }

  attemptMove(from, to) {
    // Check if it's a pawn promotion
    const piece = this.game.get(from);
    const isPromotion = piece && piece.type === 'p' && 
                       ((piece.color === 'w' && to[1] === '8') || 
                        (piece.color === 'b' && to[1] === '1'));
    
    if (isPromotion) {
      this.showPromotionModal(from, to);
      return;
    }
    
    // Try to make the move
    const move = this.game.move({ from, to });
    
    if (move) {
      this.selectedSquare = null;
      this.moveHistory.push(move);
      this.updateDisplay();
      this.checkGameEnd();
      
      // Log move to console
      console.log(`Move: ${move.san} (${from} → ${to})`);
    } else {
      // Invalid move - deselect
      this.selectedSquare = null;
      this.updateDisplay();
    }
  }

  showPromotionModal(from, to) {
    const modal = document.createElement('div');
    modal.className = 'promotion-modal';
    
    const content = document.createElement('div');
    content.className = 'promotion-content';
    
    const title = document.createElement('h3');
    title.textContent = 'Choose promotion piece:';
    content.appendChild(title);
    
    const pieces = document.createElement('div');
    pieces.className = 'promotion-pieces';
    
    const promotionOptions = ['q', 'r', 'b', 'n'];
    const currentPlayer = this.game.turn();
    
    promotionOptions.forEach(pieceType => {
      const pieceButton = document.createElement('div');
      pieceButton.className = `promotion-piece piece ${currentPlayer} ${pieceType}`;
      pieceButton.addEventListener('click', () => {
        this.makePromotionMove(from, to, pieceType);
        document.body.removeChild(modal);
      });
      pieces.appendChild(pieceButton);
    });
    
    content.appendChild(pieces);
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Close modal on background click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        document.body.removeChild(modal);
        this.selectedSquare = null;
        this.updateDisplay();
      }
    });
  }

  makePromotionMove(from, to, promotion) {
    const move = this.game.move({ from, to, promotion });
    
    if (move) {
      this.selectedSquare = null;
      this.moveHistory.push(move);
      this.updateDisplay();
      this.checkGameEnd();
      
      console.log(`Promotion move: ${move.san} (${from} → ${to})`);
    }
  }

  updateGameStatus() {
    const turnDisplay = document.getElementById('current-turn');
    const gameStatus = document.getElementById('game-status');
    
    if (this.game.game_over()) {
      if (this.game.in_checkmate()) {
        const winner = this.game.turn() === 'w' ? 'Black' : 'White';
        turnDisplay.textContent = `Checkmate! ${winner} wins`;
        gameStatus.textContent = `${winner} wins by checkmate`;
      } else if (this.game.in_draw()) {
        turnDisplay.textContent = 'Game drawn';
        gameStatus.textContent = 'Draw';
      } else if (this.game.in_stalemate()) {
        turnDisplay.textContent = 'Stalemate';
        gameStatus.textContent = 'Draw by stalemate';
      }
    } else {
      const currentPlayer = this.game.turn() === 'w' ? 'White' : 'Black';
      const checkText = this.game.in_check() ? ' (in check)' : '';
      turnDisplay.textContent = `${currentPlayer} to move${checkText}`;
      gameStatus.textContent = 'In Progress';
    }
  }

  updateMoveHistory() {
    const historyElement = document.getElementById('move-history');
    const moves = this.game.history();
    
    if (moves.length === 0) {
      historyElement.innerHTML = '<p class="text-muted">Game will begin when you make the first move...</p>';
      return;
    }
    
    let historyHTML = '';
    for (let i = 0; i < moves.length; i += 2) {
      const moveNumber = Math.floor(i / 2) + 1;
      const whiteMove = moves[i];
      const blackMove = moves[i + 1] || '';
      
      historyHTML += `
        <div class="move-pair">
          <span class="move-number">${moveNumber}.</span>
          <span class="move">${whiteMove}</span>
          ${blackMove ? `<span class="move">${blackMove}</span>` : ''}
        </div>
      `;
    }
    
    historyElement.innerHTML = historyHTML;
    historyElement.scrollTop = historyElement.scrollHeight;
  }

  updateGameInfo() {
    const moveCount = document.getElementById('move-count');
    moveCount.textContent = this.game.history().length;
  }

  checkGameEnd() {
    if (this.game.game_over()) {
      setTimeout(() => {
        this.showGameOverModal();
      }, 1000);
    }
  }

  showGameOverModal() {
    const modal = document.createElement('div');
    modal.className = 'game-over-overlay';
    
    const content = document.createElement('div');
    content.className = 'game-over-content';
    
    let title, message;
    if (this.game.in_checkmate()) {
      const winner = this.game.turn() === 'w' ? 'Black' : 'White';
      title = 'Checkmate!';
      message = `${winner} wins the game.`;
    } else if (this.game.in_draw()) {
      title = 'Game Drawn';
      message = 'The game ended in a draw.';
    } else if (this.game.in_stalemate()) {
      title = 'Stalemate';
      message = 'The game ended in a stalemate.';
    }
    
    content.innerHTML = `
      <h2>${title}</h2>
      <p>${message}</p>
      <button class="btn btn-primary" onclick="chessMatch.resetGame(); document.body.removeChild(this.closest('.game-over-overlay'))">
        New Game
      </button>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
  }

  resetGame() {
    this.game = new Chess();
    this.selectedSquare = null;
    this.moveHistory = [];
    this.updateDisplay();
    console.log('Game reset');
  }

  flipBoard() {
    this.isFlipped = !this.isFlipped;
    // For now, just recreate the board (could be enhanced with animation)
    this.createBoard();
    this.updateDisplay();
    console.log('Board flipped');
  }

  copyFEN() {
    const fen = this.game.fen();
    
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(fen).then(() => {
        this.showCopyFeedback('FEN copied to clipboard!');
      }).catch(() => {
        this.fallbackCopyFEN(fen);
      });
    } else {
      this.fallbackCopyFEN(fen);
    }
  }

  fallbackCopyFEN(fen) {
    const textArea = document.createElement('textarea');
    textArea.value = fen;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    
    try {
      textArea.select();
      document.execCommand('copy');
      this.showCopyFeedback('FEN copied to clipboard!');
    } catch (err) {
      this.showCopyFeedback('Failed to copy FEN');
    }
    
    document.body.removeChild(textArea);
  }

  showCopyFeedback(message) {
    const button = document.getElementById('copy-fen');
    const originalText = button.textContent;
    
    button.textContent = message;
    button.disabled = true;
    
    setTimeout(() => {
      button.textContent = originalText;
      button.disabled = false;
    }, 2000);
  }

  setupEventListeners() {
    // Reset game button
    document.getElementById('reset-game').addEventListener('click', () => {
      this.resetGame();
    });
    
    // Flip board button
    document.getElementById('flip-board').addEventListener('click', () => {
      this.flipBoard();
    });
    
    // Copy FEN button
    document.getElementById('copy-fen').addEventListener('click', () => {
      this.copyFEN();
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.selectedSquare = null;
        this.updateDisplay();
      } else if (e.key === 'r' && e.ctrlKey) {
        e.preventDefault();
        this.resetGame();
      } else if (e.key === 'f' && e.ctrlKey) {
        e.preventDefault();
        this.flipBoard();
      }
    });
  }
}

// Initialize the chess match when the page loads
let chessMatch;

document.addEventListener('DOMContentLoaded', function() {
  // Wait a bit to ensure chess.js is loaded
  setTimeout(() => {
    if (typeof Chess !== 'undefined') {
      chessMatch = new ChessMatch();
    } else {
      console.error('Chess.js library not loaded');
    }
  }, 100);
});