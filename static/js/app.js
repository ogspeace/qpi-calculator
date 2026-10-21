// Add / remove subject rows on the QPI form.
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("subject-rows");
  const addButton = document.getElementById("add-row");

  addButton.addEventListener("click", () => {
    const template = container.querySelector(".subject-row");
    const row = template.cloneNode(true);
    row.querySelectorAll("input").forEach((input) => (input.value = ""));
    row.querySelectorAll("select").forEach((select) => (select.selectedIndex = 0));
    container.appendChild(row);
    row.querySelector("input").focus();
  });

  container.addEventListener("click", (event) => {
    const button = event.target.closest(".remove-row");
    if (!button) return;

    const rows = container.querySelectorAll(".subject-row");
    const row = button.closest(".subject-row");
    if (rows.length > 1) {
      row.remove();
    } else {
      // Keep at least one row; just clear it.
      row.querySelectorAll("input").forEach((input) => (input.value = ""));
      row.querySelectorAll("select").forEach((select) => (select.selectedIndex = 0));
    }
  });
});

// Navbar clock: 24-hour HH:MM:SS in Philippine time. Counts from the server's clock
// rather than the device's, so it stays right even if a phone's clock is off.
(() => {
  const el = document.getElementById("ph-clock");
  const offset = Number(el.dataset.serverEpoch) * 1000 - Date.now();
  const format = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Manila", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
  });
  const parts = {};
  for (const span of el.querySelectorAll("[data-part]")) parts[span.dataset.part] = span;
  const tick = () => {
    const now = new Date(Date.now() + offset);
    const values = {};
    for (const { type, value } of format.formatToParts(now)) values[type] = value;
    for (const part of ["hour", "minute", "second"]) parts[part].textContent = values[part];
    el.dateTime = now.toISOString();
    el.setAttribute("aria-label", `Philippine time ${values.hour}:${values.minute}:${values.second}`);
  };
  tick();
  setInterval(tick, 1000);
})();

// Dark / light mode toggle; the choice is remembered on this device.
(() => {
  const button = document.getElementById("theme-toggle");
  const root = document.documentElement;
  const label = () => {
    const dark = root.getAttribute("data-bs-theme") === "dark";
    button.textContent = dark ? "\u2600\uFE0F" : "\u{1F319}"; // sun : moon
    button.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    button.title = dark ? "Light mode" : "Dark mode";
  };
  button.addEventListener("click", () => {
    const next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-bs-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) {}
    label();
  });
  label();
})();

// Same as the other sites: right-click shows "Functionality disabled."
// (Text fields keep their menu so subjects and units can still be pasted in.)
document.addEventListener("contextmenu", (e) => {
  if (e.target.closest("input, textarea, [contenteditable]")) return;
  e.preventDefault();
  alert("Functionality disabled.");
});
