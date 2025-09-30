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

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
  const resultsContainer = document.getElementById("profile-results");
  const searchInput = document.getElementById("profile-search");
  const ratingFilter = document.getElementById("rating-filter");
  const resultsCount = document.getElementById("results-count");

  // async function loadProfiles() {
  //   const search = searchInput.value.trim();
  //   const rating = ratingFilter.value;

  //   const params = new URLSearchParams({
  //     search,
  //     rating,
  //   });

  //   const response = await fetch(`/api/profiles/?${params.toString()}`);
  //   const data = await response.json();

  //   // Clear and render
  //   resultsContainer.innerHTML = "";
  //   data.profiles.forEach(profile => {
  //     const card = document.createElement("div");
  //     card.classList.add("profile-card");
  //     card.innerHTML = `
  //       <div class="profile-name">
  //         <a href="${profile.profile_url}">${profile.name}</a>
  //       </div>
  //       <div class="profile-rating">Rating: ${profile.rating}</div>
  //       <div class="profile-rank">Rank: ${profile.rank}</div>
  //     `;
  //     resultsContainer.appendChild(card);
  //   });

  //   resultsCount.textContent = `${data.profiles.length} members found`;
  // }
  async function loadProfiles() {
    const container = document.getElementById("profile-results");
    const searchEl = document.getElementById("profile-search");
    const ratingEl = document.getElementById("rating-filter");

    if (!container || !searchEl || !ratingEl) return; // ✅ exit if any not found

    const search = searchEl.value.trim();
    const rating = ratingEl.value;

    const params = new URLSearchParams({ search, rating });
    const response = await fetch(`/api/profiles/?${params.toString()}`);
    const data = await response.json();

    container.innerHTML = "";
    data.profiles.forEach(profile => {
      container.innerHTML += `
        <div class="profile-card">
          <div class="profile-name"><a href="${profile.profile_url}">${profile.name}</a></div>
          <div class="profile-rating">Rating: ${profile.rating}</div>
          <div class="profile-rank">Rank: ${profile.rank}</div>
        </div>`;
    });

    const count = document.getElementById("results-count");
    if (count) count.textContent = `${data.profiles.length} members found`;
  }

  loadProfiles();

  if(searchInput && ratingFilter){
    searchInput.addEventListener("input", () => loadProfiles());
    ratingFilter.addEventListener("change", () => loadProfiles());
  }
  // Initialize theme manager
  const themeManager = new ThemeManager();
  
  // Set active navigation
  setActiveNavigation();
  
  // Setup smooth scrolling
  setupSmoothScrolling();
  
  // Render page-specific content
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  
  switch(currentPage) {
    case 'tournaments.html':
      renderTournaments();
      break;
    case 'newsletters.html':
      renderNewsletters();
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