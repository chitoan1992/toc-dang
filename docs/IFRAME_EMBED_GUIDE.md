# Iframe Embed Guide for Gia Phả Tộc Đặng Non Nước

## Recommended Embed Code (with Fullscreen Overlay)

This solution works on both desktop and mobile browsers.

```html
<style>
  .family-tree-wrapper {
    position: relative;
    width: 100%;
  }

  .family-tree-embed {
    position: relative;
    width: 100%;
    padding-bottom: 120%;
    height: 0;
    overflow: hidden;
    border-radius: 12px;
    border: 1px solid #e8dcc9;
    background: #fdfcfa;
  }

  .family-tree-embed iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
  }

  .expand-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    z-index: 10;
    padding: 8px 12px;
    background: rgba(74, 20, 20, 0.9);
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: background 0.2s;
  }

  .expand-btn:hover {
    background: rgba(74, 20, 20, 1);
  }

  /* Fullscreen Overlay */
  .fullscreen-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 999999;
    background: #fff;
  }

  .fullscreen-overlay.active {
    display: flex;
    flex-direction: column;
  }

  .fullscreen-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    background: linear-gradient(135deg, #4a1414 0%, #731f1f 100%);
    color: #fff;
  }

  .fullscreen-title {
    font-size: 14px;
    font-weight: 600;
  }

  .close-btn {
    padding: 8px 16px;
    background: rgba(255,255,255,0.15);
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .close-btn:hover {
    background: rgba(255,255,255,0.25);
  }

  .fullscreen-body {
    flex: 1;
    position: relative;
  }

  .fullscreen-body iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
  }

  @media (min-width: 768px) {
    .family-tree-embed {
      padding-bottom: 75%;
    }
  }
</style>

<!-- Embedded View -->
<div class="family-tree-wrapper">
  <button class="expand-btn" onclick="openFamilyTree()">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
    </svg>
    Mở rộng
  </button>
  <div class="family-tree-embed">
    <iframe
      src="https://chitoan1992.github.io/toc-dang/"
      frameborder="0"
      title="Gia Phả Tộc Đặng Non Nước"
      loading="lazy"
    ></iframe>
  </div>
</div>

<!-- Fullscreen Overlay (hidden by default) -->
<div class="fullscreen-overlay" id="familyOverlay">
  <div class="fullscreen-header">
    <span class="fullscreen-title">Gia Phả Tộc Đặng Non Nước</span>
    <button class="close-btn" onclick="closeFamilyTree()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 6 6 18M6 6l12 12"/>
      </svg>
      Đóng
    </button>
  </div>
  <div class="fullscreen-body">
    <iframe
      id="fullscreenIframe"
      frameborder="0"
      title="Gia Phả Tộc Đặng Non Nước"
    ></iframe>
  </div>
</div>

<script>
function openFamilyTree() {
  const overlay = document.getElementById('familyOverlay');
  const iframe = document.getElementById('fullscreenIframe');

  // Load iframe only when opened (saves bandwidth)
  if (!iframe.src) {
    iframe.src = 'https://chitoan1992.github.io/toc-dang/';
  }

  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeFamilyTree() {
  const overlay = document.getElementById('familyOverlay');
  overlay.classList.remove('active');
  document.body.style.overflow = '';
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeFamilyTree();
  }
});
</script>
```

---

## Simple Alternative: Open in New Tab

If the overlay is too complex, use this simpler approach:

```html
<style>
  .family-tree-wrapper {
    position: relative;
    width: 100%;
  }
  .family-tree-embed {
    position: relative;
    width: 100%;
    padding-bottom: 120%;
    height: 0;
    overflow: hidden;
    border-radius: 12px;
    border: 1px solid #e8dcc9;
  }
  .family-tree-embed iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
  }
  .newtab-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    z-index: 10;
    padding: 8px 12px;
    background: rgba(74, 20, 20, 0.9);
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    text-decoration: none;
  }
  .newtab-btn:hover {
    background: rgba(74, 20, 20, 1);
    color: #fff;
  }
  @media (min-width: 768px) {
    .family-tree-embed { padding-bottom: 75%; }
  }
</style>

<div class="family-tree-wrapper">
  <a href="https://chitoan1992.github.io/toc-dang/" target="_blank" class="newtab-btn">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
      <polyline points="15 3 21 3 21 9"/>
      <line x1="10" y1="14" x2="21" y2="3"/>
    </svg>
    Mở rộng
  </a>
  <div class="family-tree-embed">
    <iframe
      src="https://chitoan1992.github.io/toc-dang/"
      frameborder="0"
      title="Gia Phả Tộc Đặng Non Nước"
      loading="lazy"
    ></iframe>
  </div>
</div>
```

---

## Aspect Ratio Comparison

| Setting | Mobile (375px) | Tablet (768px) | Desktop (1024px) |
|---------|----------------|----------------|------------------|
| `padding-bottom: 75%` (old) | 281px | 576px | 768px |
| `padding-bottom: 120%` (recommended) | **450px** | 922px | 1229px |
| `padding-bottom: 100%` | 375px | 768px | 1024px |

---

## Notes

- The Fullscreen API (`requestFullscreen()`) does NOT work on iOS Safari
- The overlay solution provides a fullscreen-like experience that works everywhere
- The iframe is lazy-loaded to improve page performance
- Press Escape key to close the overlay on desktop
