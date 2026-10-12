// End-to-end check of studio/index.html in headless Chromium.
// usage: node tests/studio_e2e.cjs <out_dir>
// Writes <out_dir>/studio_e2e.json (results + JS-generated Python per lesson) and screenshots.
// Running Python (Pyodide) needs the network, so it is covered by the harness tests in test_studio.py instead.
const path = require("path");
const fs = require("fs");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

(async () => {
  const out = process.argv[2] || "output";
  fs.mkdirSync(out, { recursive: true });
  const url = pathToFileURL(path.resolve(__dirname, "..", "studio", "index.html")).href;
  const browser = await chromium.launch();
  const result = { errors: [], lessons: {}, generated: {}, ui: {} };
  const watch = (page, tag = "") => {
    page.on("pageerror", e => result.errors.push(tag + String(e)));
    // Fonts are blocked on purpose (offline test); any other failed request or console error is a failure.
    page.on("requestfailed", r => { if (!/fonts\.(googleapis|gstatic)\.com/.test(r.url())) result.errors.push(tag + "request failed: " + r.url()); });
    page.on("console", m => { if (m.type() === "error" && !/net::ERR_FAILED/.test(m.text())) result.errors.push(tag + m.text()); });
  };
  const skipWelcome = () => { try { localStorage.setItem("blockwise-welcomed", "1"); } catch { /* ignore */ } };

  // 0. First visit: the welcome dialog opens, and its main button starts lesson 1.
  const fresh = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  watch(fresh, "fresh: ");
  await fresh.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  await fresh.goto(url);
  result.ui.welcome_on_first_visit = await fresh.isVisible("#welcome[open]");
  await fresh.screenshot({ path: path.join(out, "studio-welcome.png") });
  await fresh.click("#welcomeLearn");
  result.ui.welcome_starts_lesson = !(await fresh.isVisible("#welcome[open]"))
    && (await fresh.textContent("#lessonPanel")).includes("Your first function");
  await fresh.close();

  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  watch(page);
  await page.addInitScript(skipWelcome);
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
    result.false_connections = (result.false_connections || []).concat(
      await page.evaluate(id => connections().map(t => `${id}: ${t.title}`), id));
  }
  // Known-good templates must not trigger connection tips either.
  result.false_connections = result.false_connections.concat(await page.evaluate(() => BLOCKWISE_PRESETS.flatMap(p => {
    const values = Object.fromEntries(Object.entries(p.params).map(([k, spec]) => [k, renderValue(spec, spec.default)]));
    state.plan = normalize({ modules: [{ path: "m.py", imports: substitute(p.imports || [], values), functions: [substitute(p.function, values)] }] });
    return connections().map(t => `${p.id}: ${t.title}`);
  })));

  // 1b. Every template, with its default parameters, as the Studio would generate it.
  result.presets = await page.evaluate(() => Object.fromEntries(BLOCKWISE_PRESETS.map(p => {
    const values = Object.fromEntries(Object.entries(p.params).map(([k, spec]) => [k, renderValue(spec, spec.default)]));
    const f = substitute(p.function, values); f.requirements = []; f.body = normNodes(f.body);
    return [p.id, { plan: { format: "blockwise-plan-v1", modules: [{ path: "m.py", imports: substitute(p.imports || [], values), constants: [], functions: [f] }] },
      source: genModule({ imports: substitute(p.imports || [], values), constants: [], functions: [f] }) }];
  })));

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

  // 2b. Undo removes the last edit; redo puts it back.
  const kinds = () => page.evaluate(() => JSON.stringify(state.plan));
  const before = await kinds();
  await page.click("#undoBtn");
  const undone = await kinds();
  await page.click("#fnTitle");
  await page.keyboard.press("Control+Shift+Z");
  result.ui.undo_restores = undone !== before;
  result.ui.redo_reapplies = (await kinds()) === before;

  // 3. Wrong boundary is caught with a hint, not the answer.
  await page.locator('#builder input[aria-label="If / Else condition"]').fill("age > 18");
  await page.click("#checkWork");
  result.ui.wrong_condition_message = await page.textContent("#resultBox");

  // 4. Invalid field is flagged with a plain-language reason and not applied.
  await page.fill("#fnName", "2bad");
  result.ui.bad_name_flagged = await page.evaluate(() => document.querySelector("#fnName").classList.contains("bad") && state.plan.modules[0].functions[0].name === "can_vote");
  result.ui.bad_name_message = await page.textContent("#fieldMsg");

  // 5. Templates: filter by category, then insert one into the current file.
  await page.click("#trackLibrary");
  await page.click('#presetCats button[data-cat="auth"]');
  result.ui.preset_filter_count = await page.locator(".preset").count();
  await page.locator(".preset", { hasText: "Allow only certain roles" }).locator("button").click();
  result.ui.preset_inserted = (await page.textContent("#code")).includes("def require_admin(role: str) -> None:");

  // 5b. Concept pills open the glossary entry.
  await page.click('.tab[data-tab="lesson"]');
  await page.locator('#lessonPanel [data-word="condition"]').click();
  result.ui.glossary_jump = await page.isVisible("#word-condition.hit");

  // 5c. New blocks by clicking: a default value, a constant, and a Try / Except with a Return on each side.
  await page.evaluate(() => { state.lesson = null; state.plan = normalize({ modules: [{ path: "p.py", functions: [{ name: "to_int", parameters: [], body: [] }] }] }); state.m = 0; state.f = 0; render(); });
  await page.fill("#fnParams", "text: str, fallback: int=0");
  await page.locator("#builder details summary").click();
  await page.fill("#fnConsts", "LIMIT = 10");
  await page.locator("#palette .pal", { hasText: "Try / Except" }).click();
  await page.locator("#builder .slot:not(.root) > .add-here").nth(0).click();
  await page.locator("#builder .addmenu button", { hasText: "Return" }).click();
  await page.locator('#builder input[aria-label="Return expression"]').nth(0).fill("int(text)");
  await page.locator("#builder .slot:not(.root) > .add-here").nth(1).click();
  await page.locator("#builder .addmenu button", { hasText: "Return" }).click();
  await page.locator('#builder input[aria-label="Return expression"]').nth(1).fill("fallback");
  await page.locator('#builder input[aria-label="Try / Except exception"]').fill("ValueError, KeyError");
  result.ui.bad_exception_flagged = (await page.textContent("#fieldMsg")).includes("brackets");
  await page.locator('#builder input[aria-label="Try / Except exception"]').fill("(ValueError, TypeError)");
  result.ui.try_code = await page.evaluate(() => genModule(state.plan.modules[0]));
  result.ui.kinds_without_color = await page.evaluate(() => Object.keys(KINDS).filter(k => !getComputedStyle(document.documentElement).getPropertyValue(`--k-${k}`).trim()));
  await page.fill("#fnParams", "fallback: int=0, text: str");
  result.ui.default_order_message = await page.textContent("#fieldMsg");
  await page.screenshot({ path: path.join(out, "studio-try.png"), fullPage: true });

  // 5d. Lesson 10 by clicking: replace the TODO inside Repeat while with two Set variable blocks using += and //=.
  await page.selectOption("#lessonPick", "while-digits");
  await page.selectOption("#modePick", "guided");
  await page.click("#startLesson");
  await page.click('#builder button[aria-label="Delete block: TODO"]');
  for (const [target, op, value] of [["total", "+=", "n % 10"], ["n", "//=", "10"]]) {
    await page.locator("#builder .slot:not(.root) > .add-here").nth(0).click();
    await page.locator("#builder .addmenu button", { hasText: "Set variable" }).click();
    const count = await page.locator('#builder input[aria-label="Set variable target"]').count();
    await page.locator('#builder input[aria-label="Set variable target"]').nth(count - 1).fill(target);
    await page.locator('#builder select[aria-label="Set variable operator"]').nth(count - 1).selectOption(op);
    await page.locator('#builder input[aria-label="Set variable expression"]').nth(count - 1).fill(value);
  }
  await page.click("#checkWork");
  result.ui.while_lesson_by_clicks = (await page.textContent("#resultBox")).includes("Correct");
  await page.screenshot({ path: path.join(out, "studio-while.png"), fullPage: true });
  await page.evaluate(() => { state.plan.modules[0].functions[0].body.unshift({ kind: "break" }); render(); });
  result.ui.stray_break_tip = (await page.textContent("#tips")).includes("outside a loop");

  // 5e. Free build: New project gives a blank main() and a next-step checklist.
  await page.click("#newProject");
  await page.click("#newBlank");
  result.ui.new_project_blank = (await page.textContent("#code")).trim() === "def main() -> None:\n    pass"
    && (await page.textContent("#coach")).includes("Add blocks to main()");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: path.join(out, "studio-free-build.png") });

  // 5f. Edit tools: move a block into the If above it, back out again, and duplicate it.
  await page.locator("#palette .pal", { hasText: "If / Else" }).click();
  await page.locator("#palette .pal", { hasText: "Set variable" }).click();
  await page.click('#builder button[aria-label="Move into If / Else above: Set variable"]');
  result.ui.indent = (await page.evaluate(() => genModule(state.plan.modules[0]))).includes("    if x > 0:\n        total = 0");
  await page.click('#builder button[aria-label="Move out of this block: Set variable"]');
  await page.click('#builder button[aria-label="Duplicate block: Set variable"]');
  result.ui.outdent_duplicate = (await page.evaluate(() => genModule(state.plan.modules[0]))).includes("        pass\n    total = 0\n    total = 0");

  // 5g. Template follow-up: insert a check template, then connect it to main() in one click.
  await page.evaluate(() => { state.plan.modules[0].functions[0].body = []; render(); });
  await page.click("#trackLibrary");
  await page.click('#presetCats button[data-cat="all"]');
  await page.locator(".preset", { hasText: "Reject zero and negative numbers" }).locator("button").click();
  await page.click('.mobile-nav button[data-show="side-mid"]').catch(() => {});
  result.ui.template_card = await page.isVisible(".template-card");
  await page.screenshot({ path: path.join(out, "studio-template-card.png") });
  await page.locator(".template-card button", { hasText: "Add a call in main()" }).click();
  result.ui.template_connected = (await page.evaluate(() => genModule(state.plan.modules[0]))).includes("def main(amount: int) -> None:\n    require_positive(amount)");

  // 5h. Connection tips across files, each fixed with one click.
  await page.evaluate(() => {
    state.plan = normalize({ modules: [
      { path: "shop/checks.py", functions: [{ name: "require_positive", parameters: [{ name: "amount", type: "int" }], body: [
        { kind: "branch", condition: "amount <= 0", body: [{ kind: "raise", expression: "ValueError('amount')" }] }] }] },
      { path: "shop/cart.py", functions: [
        { name: "cart_total", parameters: [{ name: "items", type: "list" }], returns: "int", body: [
          { kind: "validate", expression: "require_positive(len(items))" }, { kind: "return", expression: "sum_prces(items)" }] },
        { name: "sum_prices", parameters: [{ name: "items", type: "list" }], returns: "int", body: [{ kind: "return", expression: "sum(i['price'] for i in items)" }] },
        { name: "unused_helper", parameters: [], returns: "int", body: [{ kind: "return", expression: "1" }] }] }] });
    state.m = 1; state.f = 0; render();
  });
  await page.click('.tab[data-tab="advice"]');
  result.ui.connection_titles = await page.locator("#tips .tip b").allTextContents();
  await page.locator("#tips .tip button", { hasText: "Add the import" }).click();
  await page.locator("#tips .tip button", { hasText: "Change to sum_prices()" }).click();
  result.ui.connections_fixed = await page.evaluate(() => connections().map(t => t.title));
  result.ui.connected_code = await page.evaluate(() => genModule(state.plan.modules[1]));

  // 6. Advisor reacts to deep nesting.
  await page.evaluate(() => {
    const deep = { kind: "branch", condition: "a", body: [{ kind: "loop", target: "i", iterable: "x", body: [{ kind: "branch", condition: "b", body: [{ kind: "branch", condition: "c", body: [{ kind: "return", expression: "1" }], otherwise: [] }], otherwise: [] }] }], otherwise: [] };
    state.plan.modules[0].functions[0].body.push(deep); render();
  });
  result.ui.advisor_text = await page.textContent("#tips");

  // 6b. A plan without optional empty lists (as Sonic or hand-written plans may have) still renders.
  await page.evaluate(() => { state.plan = normalize({ modules: [{ path: "m.py", functions: [{ name: "f", parameters: [], body: [{ kind: "branch", condition: "x", body: [{ kind: "loop", target: "i", iterable: "y" }] }] }] }] }); state.m = 0; state.f = 0; render(); });
  result.ui.sparse_plan_renders = (await page.textContent("#code")).includes("for i in y:");

  // 6c. Dark theme screenshot for review.
  await page.evaluate(() => { localStorage.clear(); localStorage.setItem("blockwise-welcomed", "1"); });
  await page.reload();
  await page.click("#themeToggle");
  await page.screenshot({ path: path.join(out, "studio-dark.png"), fullPage: true });

  // 7. Phone layout: no horizontal scroll, bottom navigation works.
  const phone = await browser.newPage({ viewport: { width: 375, height: 760 } });
  watch(phone, "phone: ");
  await phone.addInitScript(skipWelcome);
  await phone.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  await phone.goto(url);
  result.ui.phone_no_hscroll = await phone.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
  await phone.screenshot({ path: path.join(out, "studio-phone-build.png") });
  await phone.click('.mobile-nav button[data-show="side-right"]');
  result.ui.phone_nav_shows_code = await phone.isVisible("#code");
  await phone.screenshot({ path: path.join(out, "studio-phone.png") });

  await browser.close();
  fs.writeFileSync(path.join(out, "studio_e2e.json"), JSON.stringify(result, null, 2));
  console.log(JSON.stringify({ errors: result.errors, lessons: result.lessons, ui: { ...result.ui, code_after_clicks: undefined, advisor_text: result.ui.advisor_text.slice(0, 120) } }, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
