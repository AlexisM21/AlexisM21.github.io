
document.getElementById("gen").addEventListener("click", async () => {
  const raw = document.getElementById("completed").value;
  const completed = raw.split(",").map(s=>s.trim()).filter(Boolean);
  const payload = { completed };
  const res = await fetch("/schedule/next-semester", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }).catch(e=>{ alert("Failed to call backend: " + e); return; });
  if(!res) return;
  if(!res.ok){
    const txt = await res.text();
    alert("Server error: " + txt);
    return;
  }
  const data = await res.json();
  renderResults(data.data);
});

function renderResults(result){
  const container = document.getElementById("results");
  container.innerHTML = "";
  const planned = result.planned_courses || [];
  const rem = result.remaining_needed || [];
  const units = result.planned_units || 0;
  const h = document.createElement("div");
  h.innerHTML = `<div class="card"><strong>Planned Units:</strong> ${units} <br/><strong>Planned Courses:</strong> ${planned.length}</div>`;
  container.appendChild(h);

  const grid = document.createElement("div");
  grid.className = "schedule-grid";
  // simple calendar: create day columns Mon-Fri
  const days = ["Mon","Tue","Wed","Thu","Fri"];
  const cal = document.createElement("div");
  cal.className = "card";
  const header = document.createElement("h3");
  header.textContent = "Weekly Calendar (simplified)";
  cal.appendChild(header);
  const calendar = document.createElement("div");
  calendar.className = "calendar";
  days.forEach(d=>{
    const col = document.createElement("div");
    col.className = "day";
    const title = document.createElement("strong");
    title.textContent = d;
    col.appendChild(title);
    calendar.appendChild(col);
  });
  cal.appendChild(calendar);
  container.appendChild(cal);

  // put each planned course into its days
  planned.forEach(c=>{
    c.meeting.days.forEach(day=>{
      // find the day column
      const cols = container.querySelectorAll(".day");
      const idx = ["Mon","Tue","Wed","Thu","Fri"].indexOf(day);
      if(idx>=0){
        const card = document.createElement("div");
        card.style.marginTop = "6px";
        card.style.padding = "6px";
        card.style.border = "1px solid #ddd";
        card.innerHTML = `<strong>${c.course_id}</strong><br/>${c.title}<br/><small>${c.meeting.time}</small>`;
        cols[idx].appendChild(card);
      }
    });
  });

  // remaining list
  const remCard = document.createElement("div");
  remCard.className = "card";
  remCard.innerHTML = `<h3>Remaining needed (after this semester)</h3><p>${rem.join(", ") || "None"}</p>`;
  container.appendChild(remCard);
}
