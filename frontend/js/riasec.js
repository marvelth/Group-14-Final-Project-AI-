// ====== RIASEC QUESTION DATA ======
window.RIASEC_QUESTIONS = [
  { no: 1, pertanyaan: "I enjoy fixing broken items.", type: "R" },
  { no: 2, pertanyaan: "I am interested in using tools or machinery.", type: "R" },
  { no: 3, pertanyaan: "I prefer practical application over theory.", type: "R" },
  { no: 4, pertanyaan: "I enjoy assembling or building things.", type: "R" },
  { no: 5, pertanyaan: "I am interested in working outdoors rather than in an office.", type: "R" },
  { no: 6, pertanyaan: "I like understanding how equipment or technology works.", type: "R" },
  { no: 7, pertanyaan: "I like solving challenging math problems.", type: "I" },
  { no: 8, pertanyaan: "I am interested in finding out the root cause of a problem.", type: "I" },
  { no: 9, pertanyaan: "I enjoy research activities or experiments.", type: "I" },
  { no: 10, pertanyaan: "I like analyzing data before making a decision.", type: "I" },
  { no: 11, pertanyaan: "I am interested in learning how a system or technology works.", type: "I" },
  { no: 12, pertanyaan: "I enjoy finding solutions to complex problems.", type: "I" },
  { no: 13, pertanyaan: "I like drawing or designing things.", type: "A" },
  { no: 14, pertanyaan: "I enjoy creating creative artwork.", type: "A" },
  { no: 15, pertanyaan: "I am interested in art, music, film, or photography.", type: "A" },
  { no: 16, pertanyaan: "I like expressing ideas in unique ways.", type: "A" },
  { no: 17, pertanyaan: "I enjoy creating visual or multimedia content.", type: "A" },
  { no: 18, pertanyaan: "I enjoy activities that require high imagination.", type: "A" },
  { no: 19, pertanyaan: "I enjoy helping other people solve their problems.", type: "S" },
  { no: 20, pertanyaan: "I feel comfortable working in groups.", type: "S" },
  { no: 21, pertanyaan: "I like teaching or explaining things to others.", type: "S" },
  { no: 22, pertanyaan: "I am interested in social or humanitarian activities.", type: "S" },
  { no: 23, pertanyaan: "I enjoy listening to and understanding other people's feelings.", type: "S" },
  { no: 24, pertanyaan: "I feel satisfied when I can help others develop.", type: "S" },
  { no: 25, pertanyaan: "I like leading groups or organizations.", type: "E" },
  { no: 26, pertanyaan: "I am interested in running a business or enterprise.", type: "E" },
  { no: 27, pertanyaan: "I feel confident speaking in front of a large audience.", type: "E" },
  { no: 28, pertanyaan: "I like convincing other people of an idea.", type: "E" },
  { no: 29, pertanyaan: "I am interested in making important decisions within a team.", type: "E" },
  { no: 30, pertanyaan: "I enjoy looking for new opportunities to achieve goals.", type: "E" },
  { no: 31, pertanyaan: "I like creating well-organized schedules and plans.", type: "C" },
  { no: 32, pertanyaan: "I am meticulous and thorough when completing tasks.", type: "C" },
  { no: 33, pertanyaan: "I feel comfortable following established procedures.", type: "C" },
  { no: 34, pertanyaan: "I like organizing data or documents in a structured manner.", type: "C" },
  { no: 35, pertanyaan: "I enjoy work that requires high precision.", type: "C" },
  { no: 36, pertanyaan: "I enjoy ensuring that everything goes according to plan.", type: "C" }
];

window.TYPE_NAMES = {
  R: "Realistic",
  I: "Investigative",
  A: "Artistic",
  S: "Social",
  E: "Enterprising",
  C: "Conventional"
};

// ====== INITIALIZE RIASEC ======
window.initRiasec = function() {
  window.riasecAnswers = Array(window.RIASEC_QUESTIONS.length).fill(null);
  window.currentQ = 0;
  
  // Create shuffled array of question indices [0..35]
  const indices = [...Array(window.RIASEC_QUESTIONS.length).keys()];
  for (let i = indices.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [indices[i], indices[j]] = [indices[j], indices[i]];
  }
  window.shuffledQuestions = indices;
  
  window.renderQuestion();
};

// ====== RENDER QUESTION ======
window.renderQuestion = function() {
  const originalIndex = window.shuffledQuestions[window.currentQ];
  const q = window.RIASEC_QUESTIONS[originalIndex];
  const total = window.RIASEC_QUESTIONS.length;
  
  // Update UI Elements
  document.getElementById("q-type-badge").textContent = "◉ " + window.TYPE_NAMES[q.type];
  document.getElementById("q-number").textContent = `Question ${window.currentQ + 1} of ${total}`;
  document.getElementById("q-text").textContent = q.pertanyaan;
  document.getElementById("progress-label").textContent = `Question ${window.currentQ + 1} of ${total}`;
  
  const pct = Math.round((window.currentQ / total) * 100);
  document.getElementById("progress-pct").textContent = pct + "%";
  document.getElementById("progress-fill").style.width = pct + "%";
  
  // Hide Back button on the first question
  document.getElementById("btn-back").style.visibility = window.currentQ === 0 ? "hidden" : "visible";
  
  // Highlight previously saved score
  const savedScore = window.riasecAnswers[originalIndex];
  document.querySelectorAll(".answer-btn").forEach(btn => {
    btn.classList.remove("selected");
    if (savedScore !== null && parseInt(btn.dataset.score) === savedScore) {
      btn.classList.add("selected");
    }
  });
  
  // Disable next button if not answered
  document.getElementById("btn-next").disabled = (savedScore === null);
};

// ====== SELECT ANSWER ======
window.selectAnswer = function(btn) {
  document.querySelectorAll(".answer-btn").forEach(b => b.classList.remove("selected"));
  btn.classList.add("selected");
  
  const originalIndex = window.shuffledQuestions[window.currentQ];
  window.riasecAnswers[originalIndex] = parseInt(btn.dataset.score);
  
  document.getElementById("btn-next").disabled = false;
};

// ====== NEXT QUESTION ======
window.nextQuestion = function() {
  const originalIndex = window.shuffledQuestions[window.currentQ];
  if (window.riasecAnswers[originalIndex] === null) return;
  
  if (window.currentQ === window.RIASEC_QUESTIONS.length - 1) {
    // Show completion modal on last question
    document.getElementById("modal-complete").classList.add("open");
  } else {
    window.currentQ++;
    window.renderQuestion();
  }
};

// ====== PREVIOUS QUESTION ======
window.prevQuestion = function() {
  if (window.currentQ > 0) {
    window.currentQ--;
    window.renderQuestion();
  }
};
