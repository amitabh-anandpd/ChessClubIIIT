// IIIT Hyderabad Chess Club - Main JavaScript

// Sample data for realistic layouts
const sampleData = {
  players: [
    { name: "Arjun Patel", rating: 2156, delta: 1, rapid: 2145, blitz: 2089 },
    { name: "Priya Sharma", rating: 2134, delta: -1, rapid: 2167, blitz: 2098 },
    { name: "Vikash Kumar", rating: 2089, delta: 0, rapid: 2034, blitz: 2156 },
    { name: "Ananya Singh", rating: 2067, delta: 2, rapid: 2078, blitz: 2045 },
    { name: "Rohit Gupta", rating: 2034, delta: -2, rapid: 2056, blitz: 2012 },
    { name: "Meera Reddy", rating: 2021, delta: 1, rapid: 1998, blitz: 2067 },
    { name: "Karan Joshi", rating: 1987, delta: 0, rapid: 2001, blitz: 1943 },
    { name: "Sneha Iyer", rating: 1976, delta: 1, rapid: 1954, blitz: 2009 }
  ],
  
  tournaments: [
    {
      name: "IIIT Winter Championship 2025",
      date: "2025-02-15T09:00:00",
      type: "upcoming",
      format: "Classical",
      rounds: 7
    },
    {
      name: "Rapid Rating Tournament",
      date: "2025-01-25T14:00:00",
      type: "upcoming", 
      format: "Rapid",
      rounds: 5
    },
    {
      name: "Autumn Open 2024",
      date: "2024-11-15T09:00:00",
      type: "past",
      winner: "Arjun Patel",
      format: "Classical"
    },
    {
      name: "Blitz Championship 2024",
      date: "2024-10-20T16:00:00", 
      type: "past",
      winner: "Priya Sharma",
      format: "Blitz"
    }
  ],

  newsletters: [
    {
      title: "Chess Club Quarterly - Winter 2025",
      excerpt: "A comprehensive look at our recent tournaments, new member spotlights, and upcoming events for the winter season.",
      date: "2025-01-10",
      author: "Editorial Team",
      slug: "winter-2025-quarterly"
    },
    {
      title: "Mastering Endgames: Practical Tips",
      excerpt: "Essential endgame techniques every intermediate player should know, with analysis from our club experts.",
      date: "2024-12-15",
      author: "IM Rajesh Nair",
      slug: "mastering-endgames-tips"
    },
    {
      title: "Tournament Report: Autumn Open 2024",
      excerpt: "Complete coverage of our biggest tournament of the year, featuring game highlights and player interviews.",
      date: "2024-11-20",
      author: "Ananya Singh",
      slug: "autumn-open-2024-report"
    }
  ],

  matches: [
    {
      opponent: "Priya Sharma",
      result: "W",
      date: "2024-12-15",
      fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    },
    {
      opponent: "Vikash Kumar", 
      result: "L",
      date: "2024-12-10",
      fen: "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 3"
    },
    {
      opponent: "Ananya Singh",
      result: "D", 
      date: "2024-12-05",
      fen: "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2"
    }
  ]
};

// Theme Management
class ThemeManager {
  constructor() {
    this.theme = localStorage.getItem('chess-club-theme') || 'auto';
    this.init();
  }

  init() {
    this.applyTheme();
    this.setupToggle();
  }

  applyTheme() {
    const html = document.documentElement;
    
    if (this.theme === 'auto') {
      html.removeAttribute('data-theme');
    } else {
      html.setAttribute('data-theme', this.theme);
    }
    
    this.updateToggleIcon();
  }

  toggleTheme() {
    const themes = ['light', 'dark', 'auto'];
    const currentIndex = themes.indexOf(this.theme);
    this.theme = themes[(currentIndex + 1) % themes.length];
    
    localStorage.setItem('chess-club-theme', this.theme);
    this.applyTheme();
  }

  updateToggleIcon() {
    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;

    const icons = {
      light: '☀️',
      dark: '🌙', 
      auto: '🔄'
    };
    
    toggle.innerHTML = icons[this.theme] || icons.auto;
    toggle.setAttribute('aria-label', `Current theme: ${this.theme}. Click to change.`);
  }

  setupToggle() {
    const toggle = document.querySelector('.theme-toggle');
    if (toggle) {
      toggle.addEventListener('click', () => this.toggleTheme());
    }
  }
}

// Countdown Timer
class CountdownTimer {
  constructor(element, targetDate) {
    this.element = element;
    this.targetDate = new Date(targetDate);
    this.interval = null;
    this.start();
  }

  start() {
    this.update();
    this.interval = setInterval(() => this.update(), 1000);
  }

  update() {
    const now = new Date();
    const diff = this.targetDate - now;

    if (diff <= 0) {
      this.element.textContent = 'Tournament Started!';
      this.stop();
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    let display = '';
    if (days > 0) display += `${days}d `;
    if (hours > 0 || days > 0) display += `${hours}h `;
    if (minutes > 0 || hours > 0 || days > 0) display += `${minutes}m `;
    display += `${seconds}s`;

    this.element.textContent = display;
  }

  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }
}

// Copy to Clipboard functionality
function copyToClipboard(text, button) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => {
      showCopyFeedback(button, 'Copied!');
    }).catch(() => {
      fallbackCopy(text, button);
    });
  } else {
    fallbackCopy(text, button);
  }
}

function fallbackCopy(text, button) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.opacity = '0';
  document.body.appendChild(textArea);
  
  try {
    textArea.select();
    document.execCommand('copy');
    showCopyFeedback(button, 'Copied!');
  } catch (err) {
    showCopyFeedback(button, 'Failed to copy');
  }
  
  document.body.removeChild(textArea);
}

function showCopyFeedback(button, message) {
  const originalText = button.textContent;
  button.textContent = message;
  button.disabled = true;
  
  setTimeout(() => {
    button.textContent = originalText;
    button.disabled = false;
  }, 2000);
}

// Navigation active state
function setActiveNavigation() {
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(link => {
    link.classList.remove('active');
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
}

// Smooth scrolling for anchor links
function setupSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      
      if (target) {
        const headerOffset = 80;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
        });
      }
    });
  });
}

// Render functions for dynamic content
function renderLeaderboard() {
  const overallTable = document.getElementById('overall-rankings');
  const rapidTable = document.getElementById('rapid-rankings');
  const blitzTable = document.getElementById('blitz-rankings');

  if (overallTable) {
    const tbody = overallTable.querySelector('tbody');
    tbody.innerHTML = sampleData.players.map((player, index) => {
      const deltaIcon = player.delta > 0 ? '▲' : player.delta < 0 ? '▼' : '=';
      const deltaClass = player.delta > 0 ? 'badge-success' : player.delta < 0 ? 'badge-danger' : 'badge-neutral';
      
      return `
        <tr>
          <td>${index + 1}</td>
          <td><span class="badge ${deltaClass} rank-delta">${deltaIcon}</span></td>
          <td><a href="profile.html" class="match-opponent">${player.name}</a></td>
          <td><strong>${player.rating}</strong></td>
        </tr>
      `;
    }).join('');
  }

  if (rapidTable) {
    const tbody = rapidTable.querySelector('tbody');
    const rapidSorted = [...sampleData.players].sort((a, b) => b.rapid - a.rapid);
    tbody.innerHTML = rapidSorted.slice(0, 5).map((player, index) => `
      <tr>
        <td>${index + 1}</td>
        <td><a href="profile.html" class="match-opponent">${player.name}</a></td>
        <td><strong>${player.rapid}</strong></td>
      </tr>
    `).join('');
  }

  if (blitzTable) {
    const tbody = blitzTable.querySelector('tbody');
    const blitzSorted = [...sampleData.players].sort((a, b) => b.blitz - a.blitz);
    tbody.innerHTML = blitzSorted.slice(0, 5).map((player, index) => `
      <tr>
        <td>${index + 1}</td>
        <td><a href="profile.html" class="match-opponent">${player.name}</a></td>
        <td><strong>${player.blitz}</strong></td>
      </tr>
    `).join('');
  }
}

function renderTournaments() {
  const upcomingContainer = document.getElementById('upcoming-tournaments');
  const pastContainer = document.getElementById('past-tournaments');

  if (upcomingContainer) {
    const upcoming = sampleData.tournaments.filter(t => t.type === 'upcoming');
    upcomingContainer.innerHTML = upcoming.map(tournament => `
      <div class="card tournament-card">
        <div class="tournament-header">
          <div>
            <h3 class="tournament-title">${tournament.name}</h3>
            <div class="tournament-date">${new Date(tournament.date).toLocaleDateString('en-IN', {
              weekday: 'long',
              year: 'numeric', 
              month: 'long',
              day: 'numeric'
            })}</div>
            <p class="text-muted">${tournament.format} • ${tournament.rounds} rounds</p>
          </div>
          <div class="countdown" data-target="${tournament.date}">Loading...</div>
        </div>
        <div class="flex gap-4">
          <a href="#" class="btn btn-primary btn-small">Register</a>
          <a href="#" class="btn btn-secondary btn-small">View Details</a>
        </div>
      </div>
    `).join('');

    // Initialize countdowns
    document.querySelectorAll('.countdown[data-target]').forEach(element => {
      const targetDate = element.getAttribute('data-target');
      new CountdownTimer(element, targetDate);
    });
  }

  if (pastContainer) {
    const past = sampleData.tournaments.filter(t => t.type === 'past');
    pastContainer.innerHTML = past.map(tournament => `
      <div class="card tournament-card">
        <div class="tournament-header">
          <div>
            <h3 class="tournament-title">${tournament.name}</h3>
            <div class="tournament-date">${new Date(tournament.date).toLocaleDateString('en-IN', {
              year: 'numeric',
              month: 'long', 
              day: 'numeric'
            })}</div>
            <p class="text-muted">${tournament.format} • Winner: <strong>${tournament.winner}</strong></p>
          </div>
        </div>
        <div class="flex gap-4">
          <a href="#" class="btn btn-secondary btn-small">View Results</a>
          <a href="#" class="btn btn-secondary btn-small">Games Archive</a>
        </div>
      </div>
    `).join('');
  }
}

function renderNewsletters() {
  const newsletterGrid = document.querySelector('.newsletter-grid');
  
  if (newsletterGrid) {
    newsletterGrid.innerHTML = sampleData.newsletters.map(newsletter => `
      <div class="card newsletter-card">
        <div class="newsletter-image">
          <span>📰 Newsletter Image</span>
        </div>
        <div class="newsletter-meta">${new Date(newsletter.date).toLocaleDateString('en-IN')} • ${newsletter.author}</div>
        <h3 class="newsletter-title">${newsletter.title}</h3>
        <p class="newsletter-excerpt">${newsletter.excerpt}</p>
        <a href="newsletter-article.html?slug=${newsletter.slug}" class="btn btn-primary btn-small">Read More</a>
      </div>
    `).join('');
  }
}

function renderProfile() {
  const profileData = sampleData.players[0]; // Using first player as example
  
  // Render recent matches
  const matchHistory = document.getElementById('match-history');
  if (matchHistory) {
    matchHistory.innerHTML = sampleData.matches.map(match => {
      const resultClass = match.result === 'W' ? 'badge-success' : 
                         match.result === 'L' ? 'badge-danger' : 'badge-warning';
      
      return `
        <div class="match-item">
          <div class="match-info">
            <div>
              <span class="badge ${resultClass}">${match.result}</span>
              vs <a href="profile.html" class="match-opponent">${match.opponent}</a>
            </div>
            <div class="match-date">${new Date(match.date).toLocaleDateString('en-IN')}</div>
          </div>
          <button class="btn btn-secondary btn-small copy-fen" data-fen="${match.fen}">
            Copy FEN
          </button>
        </div>
      `;
    }).join('');

    // Setup copy FEN buttons
    document.querySelectorAll('.copy-fen').forEach(button => {
      button.addEventListener('click', (e) => {
        const fen = e.target.getAttribute('data-fen');
        copyToClipboard(fen, e.target);
      });
    });
  }

  // Update ratings display
  const rapidRating = document.getElementById('rapid-rating');
  const blitzRating = document.getElementById('blitz-rating');
  
  if (rapidRating) rapidRating.textContent = profileData.rapid;
  if (blitzRating) blitzRating.textContent = profileData.blitz;
}

function renderHomeHighlights() {
  // Top 3 players
  const topPlayersContainer = document.getElementById('top-players');
  if (topPlayersContainer) {
    const top3 = sampleData.players.slice(0, 3);
    topPlayersContainer.innerHTML = top3.map((player, index) => `
      <div class="flex justify-between items-center">
        <span>${index + 1}. ${player.name}</span>
        <strong>${player.rating}</strong>
      </div>
    `).join('');
  }

  // Next tournament
  const nextTournament = document.getElementById('next-tournament');
  if (nextTournament) {
    const upcoming = sampleData.tournaments.find(t => t.type === 'upcoming');
    if (upcoming) {
      nextTournament.innerHTML = `
        <h4>${upcoming.name}</h4>
        <p class="text-muted">${new Date(upcoming.date).toLocaleDateString('en-IN', {
          weekday: 'long',
          month: 'long',
          day: 'numeric'
        })}</p>
        <div class="countdown mt-2" data-target="${upcoming.date}">Loading...</div>
      `;
      
      // Initialize countdown
      const countdownEl = nextTournament.querySelector('.countdown');
      new CountdownTimer(countdownEl, upcoming.date);
    }
  }

  // Latest newsletter
  const latestNewsletter = document.getElementById('latest-newsletter');
  if (latestNewsletter) {
    const latest = sampleData.newsletters[0];
    latestNewsletter.innerHTML = `
      <h4>${latest.title}</h4>
      <p class="text-muted">${new Date(latest.date).toLocaleDateString('en-IN')}</p>
      <a href="newsletter-article.html?slug=${latest.slug}" class="btn btn-secondary btn-small mt-2">Read</a>
    `;
  }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
  // Initialize theme manager
  const themeManager = new ThemeManager();
  
  // Set active navigation
  setActiveNavigation();
  
  // Setup smooth scrolling
  setupSmoothScrolling();
  
  // Render page-specific content
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  
  switch(currentPage) {
    case 'index.html':
    case '':
      renderHomeHighlights();
      break;
    case 'leaderboard.html':
      renderLeaderboard();
      break;
    case 'tournaments.html':
      renderTournaments();
      break;
    case 'newsletters.html':
      renderNewsletters();
      break;
    case 'profile.html':
      renderProfile();
      break;
  }
  
  // Global event listeners
  document.addEventListener('click', function(e) {
    // Handle copy buttons
    if (e.target.matches('.copy-btn, .copy-fen')) {
      const text = e.target.getAttribute('data-text') || e.target.getAttribute('data-fen');
      if (text) {
        copyToClipboard(text, e.target);
      }
    }
  });
});

// Future API integration points (commented for reference)
/*
// These functions will be implemented when integrating with external APIs

async function fetchLichessData(username) {
  // Fetch user data from Lichess API
  // const response = await fetch(`https://lichess.org/api/user/${username}`);
  // return response.json();
}

async function fetchChessComData(username) {
  // Fetch user data from Chess.com API  
  // const response = await fetch(`https://api.chess.com/pub/player/${username}`);
  // return response.json();
}

async function fetchTournamentResults() {
  // Fetch tournament results from club database
  // This would connect to a backend API or database
}

async function updateRatings() {
  // Sync ratings with external platforms
  // Aggregate data from multiple sources
}
*/