// YoiBlog Default Theme - Main JS

(function() {
  'use strict';

  // === Dark/Light Theme Toggle ===
  const THEME_KEY = 'yoiblog-theme';

  function getPreferredTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
    document.querySelectorAll('.theme-icon').forEach(function(el) {
      el.textContent = theme === 'dark' ? '☀️' : '🌙';
    });
  }

  // Apply theme immediately
  setTheme(getPreferredTheme());

  document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle button
    var toggles = document.querySelectorAll('.theme-toggle');
    toggles.forEach(function(toggle) {
      toggle.addEventListener('click', function() {
        var current = document.documentElement.getAttribute('data-theme');
        setTheme(current === 'dark' ? 'light' : 'dark');
      });
    });

    // Mobile menu
    var menuBtn = document.querySelector('.mobile-menu-btn');
    var nav = document.querySelector('.nav');
    if (menuBtn && nav) {
      menuBtn.addEventListener('click', function() {
        nav.classList.toggle('open');
        menuBtn.classList.toggle('open');
      });
    }

    // === Reading Progress Bar ===
    var progressBar = document.getElementById('reading-progress');
    if (progressBar) {
      function updateProgress() {
        var scrollTop = window.scrollY;
        var docHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (docHeight > 0) {
          var percent = Math.min(100, (scrollTop / docHeight) * 100);
          progressBar.style.width = percent + '%';
        }
      }
      window.addEventListener('scroll', updateProgress, { passive: true });
      updateProgress();
    }

    // === Header shadow on scroll ===
    var header = document.querySelector('.header');
    if (header) {
      function updateHeaderShadow() {
        if (window.scrollY > 10) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      }
      window.addEventListener('scroll', updateHeaderShadow, { passive: true });
      updateHeaderShadow();
    }

    // === Back to Top ===
    var backToTop = document.getElementById('back-to-top');
    if (backToTop) {
      function updateBackToTop() {
        if (window.scrollY > 400) {
          backToTop.classList.add('visible');
        } else {
          backToTop.classList.remove('visible');
        }
      }
      window.addEventListener('scroll', updateBackToTop, { passive: true });
      updateBackToTop();

      backToTop.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    // === Copy button for code blocks ===
    document.querySelectorAll('.post-content pre').forEach(function(pre) {
      var btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.textContent = 'Copy';
      btn.style.cssText = 'position:absolute;top:10px;right:10px;padding:4px 12px;font-size:0.75rem;' +
        'border:1px solid var(--border);border-radius:6px;background:var(--bg-card);color:var(--text-muted);' +
        'cursor:pointer;opacity:0;transition:opacity 0.2s;font-family:var(--font-sans);';
      pre.style.position = 'relative';
      pre.appendChild(btn);

      pre.addEventListener('mouseenter', function() { btn.style.opacity = '1'; });
      pre.addEventListener('mouseleave', function() { btn.style.opacity = '0'; });

      btn.addEventListener('click', function() {
        var code = pre.querySelector('code');
        navigator.clipboard.writeText(code ? code.textContent : pre.textContent);
        btn.textContent = 'Copied!';
        btn.style.color = 'var(--accent)';
        btn.style.borderColor = 'var(--accent)';
        setTimeout(function() {
          btn.textContent = 'Copy';
          btn.style.color = '';
          btn.style.borderColor = '';
        }, 2000);
      });
    });

    // === Image Lightbox ===
    document.querySelectorAll('.post-content img').forEach(function(img) {
      img.addEventListener('click', function() {
        var overlay = document.createElement('div');
        overlay.className = 'lightbox-overlay';
        var clone = document.createElement('img');
        clone.src = img.src;
        clone.alt = img.alt;
        overlay.appendChild(clone);
        document.body.appendChild(overlay);

        // Trigger animation
        requestAnimationFrame(function() {
          overlay.classList.add('active');
        });

        overlay.addEventListener('click', function() {
          overlay.classList.remove('active');
          setTimeout(function() {
            overlay.remove();
          }, 300);
        });

        // Close on Escape
        function onKey(e) {
          if (e.key === 'Escape') {
            overlay.classList.remove('active');
            setTimeout(function() { overlay.remove(); }, 300);
            document.removeEventListener('keydown', onKey);
          }
        }
        document.addEventListener('keydown', onKey);
      });
    });

    // === Smooth scroll for anchor links ===
    document.querySelectorAll('a[href^="#"]').forEach(function(link) {
      link.addEventListener('click', function(e) {
        var target = document.querySelector(this.getAttribute('href'));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  });
})();
