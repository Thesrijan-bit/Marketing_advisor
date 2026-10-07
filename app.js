const form = document.getElementById("goal-form");
const goalInput = document.getElementById("goal");
const submitBtn = document.getElementById("submit-btn");
const statusEl = document.getElementById("status");
const errorEl = document.getElementById("error");
const resultsEl = document.getElementById("results");

// Example chips fill the textarea — handy when demoing live.
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    goalInput.value = chip.dataset.example;
    goalInput.focus();
  });
});

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = false;
}

function clearMessages() {
  errorEl.hidden = true;
  statusEl.hidden = true;
}

function text(tag, className, content) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  el.textContent = content; // textContent, never innerHTML — LLM output is untrusted
  return el;
}

function render(data) {
  document.getElementById("demo-banner").hidden = !data.demo_mode;
  document.getElementById("niche").textContent = data.niche_identified;
  document.getElementById("trend-summary").textContent = data.trend_summary;

  const ideasEl = document.getElementById("ideas");
  ideasEl.replaceChildren();
  data.video_ideas.forEach((idea, i) => {
    const card = document.createElement("article");
    card.className = "idea-card";
    card.append(
      text("h3", "", `${i + 1}. ${idea.title}`),
      text("p", "label", "Angle"),
      text("p", "", idea.angle),
      text("p", "label", "Why this could work"),
      text("p", "", idea.reasoning)
    );
    ideasEl.appendChild(card);
  });

  const stepsEl = document.getElementById("next-steps");
  stepsEl.replaceChildren();
  data.next_steps.forEach((step) => {
    const li = document.createElement("li");
    li.textContent = step;
    stepsEl.appendChild(li);
  });

  resultsEl.hidden = false;
  resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessages();
  resultsEl.hidden = true;

  const goal = goalInput.value.trim();
  if (!goal) {
    showError("Please type your goal first — for example: 'I want to get popular in the gaming niche on YouTube'.");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Thinking…";
  statusEl.textContent = "Asking the AI for structured advice — this can take a few seconds.";
  statusEl.hidden = false;

  try {
    const res = await fetch("/api/advice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }
    render(data);
  } catch (err) {
    showError("Couldn't reach the server. Is the Flask app still running? Please try again.");
  } finally {
    statusEl.hidden = true;
    submitBtn.disabled = false;
    submitBtn.textContent = "Get video ideas";
  }
});
