const tokenKey = "nexgile_access_token";
const $ = (selector) => document.querySelector(selector);

const money = (value) => new Intl.NumberFormat("en-IN", {
  style: "currency", currency: "INR", maximumFractionDigits: 0,
}).format(Number(value || 0));

const number = (value) => new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(Number(value || 0));

function setError(id, message) {
  const element = $(id);
  element.textContent = message;
  element.hidden = !message;
}

async function api(path) {
  const response = await fetch(path, {
    headers: { Authorization: `Bearer ${localStorage.getItem(tokenKey)}` },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "We couldn't load your account information.");
  return data;
}

function empty(container, message) {
  container.replaceChildren();
  const element = document.createElement("p");
  element.className = "empty-state";
  element.textContent = message;
  container.append(element);
}

function renderSummary(summary) {
  const cards = [ ["Available cash", summary.cash], ["Portfolio value", summary.portfolio_value], ["Total assets", summary.total_assets] ];
  const container = $("#summary-cards");
  container.replaceChildren();
  cards.forEach(([label, amount]) => {
    const card = document.createElement("article"); card.className = "summary-card";
    const cardLabel = document.createElement("div"); cardLabel.className = "label"; cardLabel.textContent = label;
    const value = document.createElement("div"); value.className = "amount"; value.textContent = money(amount);
    card.append(cardLabel, value); container.append(card);
  });
}

function renderRisk(risk) {
  const container = $("#risk-content"); container.replaceChildren();
  if (!risk) return empty(container, "Complete a risk profile to see your investment style.");
  const score = document.createElement("div"); score.className = "risk-score";
  const numberEl = document.createElement("strong"); numberEl.textContent = risk.score;
  const label = document.createElement("span"); label.textContent = "risk score"; score.append(numberEl, label);
  const tag = document.createElement("span"); const category = String(risk.category || "Unknown");
  tag.className = `risk-tag ${category.toLowerCase()}`; tag.textContent = category;
  container.append(score, tag);
}

function renderHoldings(holdings) {
  const body = $("#holdings-body"); body.replaceChildren(); $("#holding-count").textContent = `${holdings.length} asset${holdings.length === 1 ? "" : "s"}`;
  if (!holdings.length) { const row = document.createElement("tr"); const cell = document.createElement("td"); cell.colSpan = 5; cell.className = "empty-state"; cell.textContent = "No holdings have been added yet."; row.append(cell); body.append(row); return; }
  holdings.forEach((holding) => { const row = document.createElement("tr"); [holding.symbol, number(holding.quantity), money(holding.average_cost), money(holding.current_price), money(holding.market_value)].forEach((value) => { const cell = document.createElement("td"); cell.textContent = value; row.append(cell); }); body.append(row); });
}

function renderGoals(goals) {
  const container = $("#goals-list"); container.replaceChildren(); if (!goals.length) return empty(container, "No financial goals have been created yet.");
  goals.forEach((goal) => { const progressData = goal.progress || goal; const percentage = Math.min(100, Math.max(0, Number(progressData.progress_percentage || 0))); const item = document.createElement("article"); item.className = "goal-item";
    const top = document.createElement("div"); top.className = "item-top"; const name = document.createElement("span"); name.textContent = goal.name; const percent = document.createElement("span"); percent.textContent = `${percentage.toFixed(1)}%`; top.append(name, percent);
    const meta = document.createElement("div"); meta.className = "item-meta"; meta.textContent = `${money(progressData.current_amount)} of ${money(progressData.target_amount)} · ${money(goal.monthly_requirement)} / month`;
    const track = document.createElement("div"); track.className = "progress-track"; const fill = document.createElement("span"); fill.style.width = `${percentage}%`; track.append(fill); item.append(top, meta, track); container.append(item); });
}

function renderTransactions(transactions) {
  const container = $("#transactions-list"); container.replaceChildren(); if (!transactions.length) return empty(container, "No transactions have been recorded yet.");
  transactions.slice(0, 6).forEach((transaction) => { const item = document.createElement("article"); item.className = "transaction-item"; const top = document.createElement("div"); top.className = "item-top"; const type = document.createElement("span"); type.className = "transaction-type"; type.textContent = transaction.transaction_type; const amount = document.createElement("span"); const isCredit = ["DEPOSIT", "SELL", "DIVIDEND"].includes(transaction.transaction_type); amount.className = isCredit ? "positive" : "negative"; amount.textContent = `${isCredit ? "+" : "−"}${money(transaction.amount)}`; top.append(type, amount); const meta = document.createElement("div"); meta.className = "item-meta"; meta.textContent = new Date(transaction.transaction_date).toLocaleDateString("en-IN", { dateStyle: "medium" }); item.append(top, meta); container.append(item); });
}

async function loadDashboard() {
  setError("#dashboard-error", ""); $("#refresh-button").disabled = true;
  try {
    const [dashboard, holdings, transactions] = await Promise.all([api("/api/dashboard/client/full"), api("/api/holdings/client"), api("/api/transactions/")]);
    const clientName = dashboard.client?.name || "Client"; $("#client-name").textContent = clientName; $("#greeting").textContent = `Hello, ${clientName.split(" ")[0]}`;
    renderSummary(dashboard.financial_summary || {}); renderRisk(dashboard.risk_profile); renderHoldings(holdings); renderGoals(dashboard.goals || []); renderTransactions(transactions);
  } catch (error) {
    if (/token|expired|access denied|user not found/i.test(error.message)) logout(); else setError("#dashboard-error", error.message);
  } finally { $("#refresh-button").disabled = false; }
}

function showDashboard() { $("#login-view").hidden = true; $("#dashboard-view").hidden = false; loadDashboard(); }
function logout() { localStorage.removeItem(tokenKey); $("#dashboard-view").hidden = true; $("#login-view").hidden = false; $("#password").value = ""; }

$("#login-form").addEventListener("submit", async (event) => { event.preventDefault(); setError("#login-error", ""); const button = $("#login-button"); button.disabled = true;
  try { const response = await fetch("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: $("#email").value.trim(), password: $("#password").value }) }); const data = await response.json().catch(() => ({})); if (!response.ok || !data.access_token) throw new Error(data.error || "Sign-in failed. Check your email and password."); localStorage.setItem(tokenKey, data.access_token); showDashboard(); } catch (error) { setError("#login-error", error.message); } finally { button.disabled = false; } });
$("#refresh-button").addEventListener("click", loadDashboard); $("#logout-button").addEventListener("click", logout);
if (localStorage.getItem(tokenKey)) showDashboard();
