// ====== STATE VARIABLES ======
window.userData = { nama: "", kelas: "" };
window.nilaiData = {
  math: 75,
  indonesian: 75,
  english: 75,
  biology: 75,
  physics: 75,
  chemistry: 75,
  economics: 75,
  sociology: 75
};
window.prestasiVal = 0;
window.bidangPrestasi = "";
window.minatList = [];
window.riasecAnswers = Array(36).fill(null);
window.shuffledQuestions = []; // Array of indices mapping to original question indices
window.currentQ = 0;

// ====== CONFIGURATION CONSTANTS ======
window.NILAI_MAPEL = [
  { key: "math", label: "Mathematics" },
  { key: "english", label: "English" },
  { key: "indonesian", label: "Indonesian" },
  { key: "physics", label: "Physics" },
  { key: "chemistry", label: "Chemistry" },
  { key: "biology", label: "Biology" },
  { key: "economics", label: "Economics" },
  { key: "sociology", label: "Sociology" }
];

// ====== PAGE NAVIGATION ======
window.showPage = function(id) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  const targetPage = document.getElementById(id);
  if (targetPage) {
    targetPage.classList.add("active");
  }
  window.scrollTo(0, 0);
};

// ====== LANDING ======
window.openDisclaimer = function() {
  document.getElementById("modal-disclaimer").classList.add("open");
};

window.startAkademik = function() {
  const nameInput = document.getElementById("input-nama");
  const gradeSelect = document.getElementById("input-kelas");
  
  const nama = nameInput.value.trim();
  const kelas = gradeSelect.value;
  
  if (!nama) {
    alert("Please enter your name!");
    return;
  }
  if (!kelas) {
    alert("Please select your grade!");
    return;
  }
  
  window.userData = { nama, kelas };
  document.getElementById("modal-disclaimer").classList.remove("open");
  
  window.buildNilaiGrid();
  window.showPage("page-akademik");
};

// ====== ACADEMIC ======
window.buildNilaiGrid = function() {
  const grid = document.getElementById("nilai-grid");
  if (!grid) return;
  
  grid.innerHTML = window.NILAI_MAPEL.map(m => `
    <div class="nilai-item">
      <label>${m.label}</label>
      <div class="nilai-counter">
        <button onclick="window.changeNilai('${m.key}', -1)">−</button>
        <input type="number" id="nilai-${m.key}" value="${window.nilaiData[m.key]}" min="0" max="100"
          onchange="window.updateNilaiInput('${m.key}', this.value)"/>
        <button onclick="window.changeNilai('${m.key}', 1)">+</button>
      </div>
    </div>
  `).join("");
};

window.changeNilai = function(key, delta) {
  window.nilaiData[key] = Math.max(0, Math.min(100, window.nilaiData[key] + delta));
  const inputEl = document.getElementById("nilai-" + key);
  if (inputEl) {
    inputEl.value = window.nilaiData[key];
  }
};

window.updateNilaiInput = function(key, val) {
  let parsed = parseInt(val) || 0;
  parsed = Math.max(0, Math.min(100, parsed));
  window.nilaiData[key] = parsed;
  const inputEl = document.getElementById("nilai-" + key);
  if (inputEl) {
    inputEl.value = parsed;
  }
};

window.selectPrestasi = function(el) {
  document.querySelectorAll("#prestasi-options .pill-option").forEach(p => p.classList.remove("active"));
  el.classList.add("active");
  window.prestasiVal = parseInt(el.dataset.val);
  
  const bidangSection = document.getElementById("bidang-section");
  if (bidangSection) {
    bidangSection.style.display = window.prestasiVal > 0 ? "block" : "none";
  }
  if (window.prestasiVal === 0) {
    window.bidangPrestasi = "";
    document.querySelectorAll("#bidang-options .bidang-option").forEach(b => b.classList.remove("active"));
  }
};

window.selectBidang = function(el) {
  document.querySelectorAll("#bidang-options .bidang-option").forEach(b => b.classList.remove("active"));
  el.classList.add("active");
  window.bidangPrestasi = el.dataset.val;
};

window.toggleMinat = function(el) {
  const val = el.dataset.val;
  if (el.classList.contains("active")) {
    el.classList.remove("active");
    window.minatList = window.minatList.filter(v => v !== val);
  } else {
    if (window.minatList.length >= 3) {
      const countEl = document.getElementById("minat-count");
      if (countEl) {
        countEl.classList.add("warn");
        setTimeout(() => countEl.classList.remove("warn"), 1200);
      }
      return;
    }
    el.classList.add("active");
    window.minatList.push(val);
  }
  
  const countEl = document.getElementById("minat-count");
  if (countEl) {
    countEl.textContent = `${window.minatList.length} / 3 fields selected`;
  }
};

window.goToRiasec = function() {
  window.showPage("page-riasec");
  if (typeof window.initRiasec === 'function') {
    window.initRiasec();
  }
};

// ====== RESULTS API CALL ======
window.computeRiasec = function() {
  const scores = { R: 0, I: 0, A: 0, S: 0, E: 0, C: 0 };
  window.RIASEC_QUESTIONS.forEach((q, idx) => {
    const score = window.riasecAnswers[idx];
    if (score !== null) {
      scores[q.type] += score;
    }
  });
  return scores;
};

window.analyzeWithAI = async function() {
  const riasec = window.computeRiasec();
  
  const requestData = {
    nama: window.userData.nama,
    kelas: window.userData.kelas,
    nilai: {
      math: window.nilaiData.math,
      indonesian: window.nilaiData.indonesian,
      english: window.nilaiData.english,
      biology: window.nilaiData.biology,
      physics: window.nilaiData.physics,
      chemistry: window.nilaiData.chemistry,
      economics: window.nilaiData.economics,
      sociology: window.nilaiData.sociology
    },
    riasec: {
      'R': riasec.R,
      'I': riasec.I,
      'A': riasec.A,
      'S': riasec.S,
      'E': riasec.E,
      'C': riasec.C
    },
    prestasi: window.prestasiVal,
    bidang_prestasi: window.bidangPrestasi,
    minat: window.minatList
  };

  try {
    const resp = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData)
    });
    
    if (!resp.ok) {
      const errorData = await resp.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error ${resp.status}`);
    }
    
    const result = await resp.json();
    if (result.success && result.top3) {
      if (typeof window.renderHasil === 'function') {
        window.renderHasil(result.top3, riasec);
      }
    } else {
      throw new Error("Invalid response format received from server.");
    }
  } catch (e) {
    console.error("KNN Analysis Error:", e);
    const contentEl = document.getElementById("hasil-content");
    if (contentEl) {
      contentEl.innerHTML = `
        <div style="text-align:center; padding:80px 24px;">
          <div style="font-size:54px; margin-bottom:24px;">😔</div>
          <p style="color:var(--ink-soft); font-weight:600; font-size:16px;">An error occurred during analysis</p>
          <p style="color:var(--ink-soft); font-size:13px; margin-top:8px;">${e.message}</p>
          <p style="color:var(--ink-soft); font-size:12px; margin-top:16px;">
            <strong>💡 Tip:</strong> Please verify that the Flask server backend is up and running on port 5001.
          </p>
          <button class="btn-restart" onclick="location.reload()">Restart</button>
        </div>
      `;
    }
  }
};
