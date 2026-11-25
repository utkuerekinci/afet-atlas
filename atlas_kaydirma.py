"""Sabit sağ-alt sayfa gezinme butonu (yalnızca genel arayüz için)."""
from __future__ import annotations

import streamlit as st

# Tamamen sabit HTML/JS: kullanıcı verisi, GitHub anahtarı veya API anahtarı yok.
_SCROLL_NAV = r"""
<script>
(() => {
  const id = 'afet-atlas-sayfa-kaydir';
  if (typeof window.__afetAtlasScrollCleanup === 'function') {
    window.__afetAtlasScrollCleanup();
  }
  const button = document.createElement('button');
  button.id = id;
  button.type = 'button';
  button.setAttribute('aria-label', 'Sayfanın altına kaydır');
  button.setAttribute('title', 'Aşağı kaydır');
  button.style.cssText = [
    'position:fixed', 'bottom:max(22px, env(safe-area-inset-bottom))',
    'right:max(22px, env(safe-area-inset-right))', 'z-index:99999',
    'width:52px', 'height:52px', 'display:flex',
    'align-items:center', 'justify-content:center',
    'border:1px solid #ff91a2', 'border-radius:16px',
    'background:#f04e66', 'color:#ffffff',
    'box-shadow:0 8px 24px rgba(0,0,0,.34)',
    'cursor:pointer', 'transition:background-color .15s ease, transform .15s ease'
  ].join(';');
  const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  icon.setAttribute('viewBox', '0 0 24 24');
  icon.setAttribute('width', '25');
  icon.setAttribute('height', '25');
  icon.setAttribute('fill', 'none');
  icon.setAttribute('stroke', 'currentColor');
  icon.setAttribute('stroke-width', '2.6');
  icon.setAttribute('stroke-linecap', 'round');
  icon.setAttribute('stroke-linejoin', 'round');
  icon.setAttribute('aria-hidden', 'true');
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  icon.appendChild(path);
  button.appendChild(icon);
  button.addEventListener('mouseenter', () => { button.style.background = '#ff667e'; });
  button.addEventListener('mouseleave', () => { button.style.background = '#f04e66'; });
  document.body.appendChild(button);

  const selectors = [
    'section[data-testid="stMain"]',
    '[data-testid="stMain"]',
    '[data-testid="stAppViewContainer"]',
    'section.main',
    'main'
  ];
  function scroller() {
    for (const selector of selectors) {
      const node = document.querySelector(selector);
      if (node && node.scrollHeight > node.clientHeight + 30) return node;
    }
    return document.scrollingElement || document.documentElement;
  }
  let active = null;
  function update() {
    const node = scroller();
    if (node !== active) {
      if (active) active.removeEventListener('scroll', update);
      active = node;
      active.addEventListener('scroll', update, {passive:true});
    }
    const up = node.scrollTop > 180;
    button.dataset.direction = up ? 'up' : 'down';
    path.setAttribute('d', up ? 'M12 19V5 M5 12l7-7 7 7' : 'M12 5v14 M5 12l7 7 7-7');
    button.setAttribute('aria-label', up ? 'Sayfanın başına kaydır' : 'Sayfanın altına kaydır');
    button.title = up ? 'Yukarı kaydır' : 'Aşağı kaydır';
    button.style.display = node.scrollHeight > node.clientHeight + 30 ? 'flex' : 'none';
  }
  button.addEventListener('click', () => {
    const node = scroller();
    const down = button.dataset.direction !== 'up';
    node.scrollTo({top: down ? node.scrollHeight : 0, behavior: 'smooth'});
  });
  window.addEventListener('resize', update, {passive:true});
  const observer = new MutationObserver(() => { window.requestAnimationFrame(update); });
  const root = document.querySelector('[data-testid="stApp"]') || document.body;
  observer.observe(root, {childList:true, subtree:true});
  window.__afetAtlasScrollCleanup = () => {
    observer.disconnect();
    window.removeEventListener('resize', update);
    if (active) active.removeEventListener('scroll', update);
    button.remove();
  };
  window.requestAnimationFrame(update);
})();
</script>
"""


def kaydirma_butonu() -> None:
    """Üstte aşağı, kaydırınca yukarı yönlenen sabit kırmızı düğmeyi ekle."""
    st.html(_SCROLL_NAV, unsafe_allow_javascript=True)
