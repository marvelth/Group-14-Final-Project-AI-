// ====== RESULTS ROUTING ======
window.goToHasil = function() {
  document.getElementById("modal-complete").classList.remove("open");
  
  const chipEl = document.getElementById("hasil-user-chip");
  if (chipEl) {
    chipEl.textContent = `👤 ${window.userData.nama} — Grade ${window.userData.kelas}`;
  }
  
  window.showPage("page-hasil");
  window.analyzeWithAI();
};

// ====== RENDER RESULTS ======
window.renderHasil = function(top3, riasec) {
  const rankClass = ["rank1", "rank2", "rank3"];
  const rankSymbol = ["🥇", "🥈", "🥉"];
  const maxRiasec = 30; // Max score for 6 questions is 6 * 5 = 30
  
  // Build recommended major cards
  const cardsHTML = top3.map((item, idx) => `
    <div class="top-card ${rankClass[idx]}">
      <div class="rank-badge">${rankSymbol[idx]}</div>
      <div class="card-info">
        <h3>${item.jurusan}</h3>
        <div class="bidang-tag">${item.bidang}</div>
        <p class="alasan">${item.alasan}</p>
      </div>
      <div class="percent-ring">
        ${window.buildRing(item.persen)}
        <div class="pct-label">Match Rate</div>
      </div>
    </div>
  `).join("");
  
  // Sort and build RIASEC profile bars
  const riasecKeys = {
    R: "Realistic (R)",
    I: "Investigative (I)",
    A: "Artistic (A)",
    S: "Social (S)",
    E: "Enterprising (E)",
    C: "Conventional (C)"
  };
  
  const topRiasecSorted = Object.entries(riasec).sort((a, b) => b[1] - a[1]);
  const riasecBarsHTML = topRiasecSorted.map(([key, val]) => {
    const label = riasecKeys[key] || key;
    const pct = Math.round((val / maxRiasec) * 100);
    return `
      <div class="riasec-bar-item">
        <span class="bar-label">${label}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
        <span class="bar-val">${val}</span>
      </div>
    `;
  }).join("");
  
  const contentEl = document.getElementById("hasil-content");
  if (contentEl) {
    contentEl.innerHTML = `
      ${cardsHTML}
      
      <div class="riasec-breakdown">
        <h4>Your RIASEC Interest Profile</h4>
        <div class="riasec-bars">${riasecBarsHTML}</div>
      </div>
      
      <div class="bk-notice">
        <span class="notice-icon">💬</span>
        <p>
          <strong>Guidance Counselor Consultation Notice:</strong> These recommendations are initial guides based on your input. We strongly advise sharing these results with your <strong>school guidance counselor</strong> or parents to formulate a balanced and thorough academic plan.
        </p>
      </div>
      
      <button class="btn-restart" onclick="location.reload()">Take Test Again</button>
      <div style="height:48px"></div>
    `;
  }
};

// ====== BUILD SVG PERCENTAGE RING ======
window.buildRing = function(pct) {
  const r = 28, cx = 36, cy = 36;
  const circ = 2 * Math.PI * r;
  const dash = (circ * pct) / 100;
  return `
    <svg viewBox="0 0 72 72">
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="5"/>
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#6D5DFC" stroke-width="5"
        stroke-dasharray="${dash} ${circ}" stroke-dashoffset="${circ / 4}" stroke-linecap="round"/>
      <text x="${cx}" y="${cy + 5}" text-anchor="middle" class="pct-text" font-size="13" font-weight="800" fill="#FFF" font-family="'Plus Jakarta Sans',sans-serif">${pct}%</text>
    </svg>
  `;
};
