// End-to-end check of studio/index.html in headless Chromium.
// usage: node tests/studio_e2e.cjs <out_dir>
// Writes <out_dir>/studio_e2e.json (results + JS-generated Python per lesson) and screenshots.
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

(async () => {
  const out = process.argv[2] || "output";
  fs.mkdirSync(out, { recursive: true });
  const url = "file://" + path.resolve(__dirname, "..", "studio", "index.html");
  const browser = await chromium.launch();
  const result = { errors: [], lessons: {}, generated: {}, ui: {} };
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  page.on("pageerror", e => result.errors.push(String(e)));
  // Fonts are blocked on purpose (offline test); any other failed request or console error is a failure.
  page.on("requestfailed", r => { if (!/fonts\.(googleapis|gstatic)\.com/.test(r.url())) result.errors.push("request failed: " + r.url()); });
  page.on("console", m => { if (m.type() === "error" && !/net::ERR_FAILED/.test(m.text())) result.errors.push(m.text()); });
  await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  await page.goto(url);

  // 1. Every lesson: guided start is "not yet"; the official solution checks as correct; record generated Python.
  const ids = await page.evaluate(() => BLOCKWISE_LESSONS.map(l => l.id));
  for (const id of ids) {
    await page.selectOption("#lessonPick", id);
    await page.selectOption("#modePick", "guided");
    await page.click("#startLesson");
    await page.click("#checkWork");
    const guided = await page.textContent("#resultBox");
    await page.evaluate(id => { state.plan = JSON.parse(JSON.stringify(BLOCKWISE_LESSONS.find(l => l.id === id).solution)); render(); }, id);
    await page.click("#checkWork");
    const solved = await page.textContent("#resultBox");
    result.lessons[id] = { guided_not_yet: guided.includes("Not yet"), solution_correct: solved.includes("Correct") };
    result.generated[id] = await page.evaluate(() => Object.fromEntries(state.plan.modules.map(m => [m.path, genModule(m)])));
  }

  // 2. Real clicks: lesson 2 (if / else) built through the UI.
  await page.selectOption("#lessonPick", "if-else");
  await page.click("#startLesson");
  const slots = page.locator("#builder .slot:not(.root) > .add-here");
  await slots.nth(0).click();
  await page.locator("#builder .addmenu button", { hasText: "Return" }).click();
  await page.locator('#builder input[aria-label="Return expression"]').nth(0).fill("True");
  await page.locator("#builder .slot:not(.root) > .add-here").nth(1).click();
  await page.locator("#builder .addmenu button", { hasText: "Return" }).click();
  await page.locator('#builder input[aria-label="Return expression"]').nth(1).fill("False");
  await page.click("#checkWork");
  result.ui.clicked_lesson_correct = (await page.textContent("#resultBox")).includes("Correct");
  result.ui.code_after_clicks = await page.textContent("#code");
  await page.screenshot({ path: path.join(out, "studio-desktop.png"), fullPage: true });

  // 3. Wrong boundary is caught with a hint, not the answer.
  await page.locator('#builder input[aria-label="If / Else condition"]').fill("age > 18");
  await page.click("#checkWork");
  result.ui.wrong_condition_message = await page.textContent("#resultBox");

  // 4. Invalid field is flagged and not applied.
  await page.fill("#fnName", "2bad");
  result.ui.bad_name_flagged = await page.evaluate(() => document.querySelector("#fnName").classList.contains("bad") && state.plan.modules[0].functions[0].name === "can_vote");

  // 5. Insert a preset into the current file.
  await page.click('.tab[data-tab="presets"]');
  await page.locator(".preset", { hasText: "Allow only certain roles" }).locator("button").click();
  result.ui.preset_inserted = (await page.textContent("#code")).includes("def require_admin(role: str) -> None:");

  // 6. Advisor reacts to deep nesting.
  await page.evaluate(() => {
    const deep = { kind: "branch", condition: "a", body: [{ kind: "loop", target: "i", iterable: "x", body: [{ kind: "branch", condition: "b", body: [{ kind: "branch", condition: "c", body: [{ kind: "return", expression: "1" }], otherwise: [] }], otherwise: [] }] }], otherwise: [] };
    state.plan.modules[0].functions[0].body.push(deep); render();
  });
  result.ui.advisor_text = await page.textContent("#tips");

  // 6b. A plan without optional empty lists (as Sonic or hand-written plans may have) still renders.
  await page.evaluate(() => { state.plan = normalize({ modules: [{ path: "m.py", functions: [{ name: "f", parameters: [], body: [{ kind: "branch", condition: "x", body: [{ kind: "loop", target: "i", iterable: "y" }] }] }] }] }); state.m = 0; state.f = 0; render(); });
  result.ui.sparse_plan_renders = (await page.textContent("#code")).includes("for i in y:");

  // 7. Phone layout: no horizontal scroll, bottom navigation works.
  const phone = await browser.newPage({ viewport: { width: 375, height: 760 } });
  phone.on("pageerror", e => result.errors.push("phone: " + String(e)));
  await phone.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  await phone.goto(url);
  result.ui.phone_no_hscroll = await phone.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
  await phone.click('.mobile-nav button[data-show="side-right"]');
  result.ui.phone_nav_shows_code = await phone.isVisible("#code");
  await phone.screenshot({ path: path.join(out, "studio-phone.png") });

  await browser.close();
  fs.writeFileSync(path.join(out, "studio_e2e.json"), JSON.stringify(result, null, 2));
  console.log(JSON.stringify({ errors: result.errors, lessons: result.lessons, ui: { ...result.ui, code_after_clicks: undefined, advisor_text: result.ui.advisor_text.slice(0, 120) } }, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
