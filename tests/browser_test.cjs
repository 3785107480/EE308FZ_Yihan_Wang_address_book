/* Real UI -> intercepted transport -> Python WSGI app -> isolated SQLite. */
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const readline = require('node:readline');
const { chromium } = require('playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'addressbook-browser-'));
  const python = process.env.ADDRESSBOOK_PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
  const bridge = spawn(python, [path.join(__dirname, 'browser_bridge.py'), path.join(directory, 'test.db')], { cwd: root });
  const queue = [];
  let stderr = '';
  bridge.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
  bridge.on('error', (error) => { for (const item of queue.splice(0)) item.reject(error); });
  bridge.on('exit', (code) => { for (const item of queue.splice(0)) item.reject(new Error(`Python bridge exited (${code}): ${stderr}`)); });
  readline.createInterface({ input: bridge.stdout }).on('line', (line) => {
    const item = queue.shift();
    if (!item) return;
    try {
      const result = JSON.parse(line);
      if (result.bridge_error) item.reject(new Error(result.bridge_error));
      else item.resolve(result);
    } catch (error) { item.reject(error); }
  });
  const send = (request) => new Promise((resolve, reject) => {
    queue.push({ resolve, reject });
    bridge.stdin.write(`${JSON.stringify(request)}\n`);
  });
  let browser;
  try {
    browser = await chromium.launch(process.env.ADDRESSBOOK_CHROME ? { executablePath: process.env.ADDRESSBOOK_CHROME } : {});
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    const page = await context.newPage();
    page.on('pageerror', (error) => errors.push(error.message));
    await context.route('http://addressbook.test/**', async (route) => {
      const request = route.request();
      const url = new URL(request.url());
      const result = await send({ method: request.method(), path: url.pathname, query: url.search.slice(1), headers: request.headers(), body: (request.postDataBuffer() || Buffer.alloc(0)).toString('base64') });
      await route.fulfill({ status: result.status, headers: result.headers, body: Buffer.from(result.body, 'base64') });
    });
    const until = async (check, description) => {
      for (let i = 0; i < 100; i++) {
        if (await check()) return;
        await page.waitForTimeout(50);
      }
      throw new Error(`Timed out: ${description}`);
    };
    await page.goto('http://addressbook.test/');
    await until(async () => (await page.locator('#connection-text').innerText()) === 'Connected', 'initial connection');
    assert.match(await page.locator('#contact-list').innerText(), /Every connection starts here/);
    await page.getByRole('button', { name: 'Add contact', exact: true }).click();
    await page.locator('#contact-name').fill('Browser Test Contact');
    await page.locator('[name="company"]').fill('FZU–MU');
    await page.locator('.method-value-input').fill('00123456789');
    await page.getByRole('button', { name: 'Add method', exact: false }).click();
    await page.locator('.method-type').nth(1).selectOption('email');
    await page.locator('.method-label').nth(1).fill('University');
    await page.locator('.method-value-input').nth(1).fill('browser@example.com');
    await page.locator('[name="bookmarked"]').check();
    await page.getByRole('button', { name: 'Save contact', exact: true }).click();
    await until(async () => await page.locator('#contact-dialog').evaluate((node) => !node.open), 'contact save');
    assert.match(await page.locator('#contact-detail').innerText(), /00123456789/);
    assert.match(await page.locator('#contact-detail').innerText(), /browser@example.com/);
    await page.reload();
    await until(async () => (await page.locator('#stat-total').innerText()) === '1', 'persistence after reload');
    await page.locator('#bookmarks-view').click();
    assert.equal(await page.locator('.contact-row').count(), 1);
    await page.locator('#search').fill('nobody matches');
    assert.match(await page.locator('#contact-list').innerText(), /No matches/);
    await page.locator('#search').fill('');
    await page.getByRole('button', { name: 'View Browser Test Contact', exact: true }).click();
    await page.getByRole('button', { name: 'Edit contact', exact: true }).click();
    await page.locator('[name="job_title"]').fill('Verified by browser');
    await page.getByRole('button', { name: 'Save changes', exact: true }).click();
    await until(async () => await page.locator('#contact-dialog').evaluate((node) => !node.open), 'contact edit');
    assert.match(await page.locator('#contact-detail').innerText(), /Verified by browser/);
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#export-button').click();
    const download = await downloadPromise;
    const exported = path.join(directory, 'roundtrip.xlsx');
    await download.saveAs(exported);
    assert.equal((await fs.readFile(exported)).subarray(0, 2).toString(), 'PK');
    await page.getByRole('button', { name: 'Delete contact', exact: true }).click();
    await page.locator('#confirm-delete').click();
    await until(async () => (await page.locator('#stat-total').innerText()) === '0', 'deletion');
    await page.locator('#open-import').click();
    await page.locator('#import-file').setInputFiles(exported);
    await page.locator('#start-import').click();
    await until(async () => !(await page.locator('#import-result').isHidden()), 'Excel restore');
    assert.match(await page.locator('#import-result').innerText(), /1 contact imported/);
    await page.locator('#import-file').setInputFiles(exported);
    await page.locator('#start-import').click();
    await until(async () => (await page.locator('#import-result').innerText()).includes('0 contacts imported'), 'duplicate skip');
    await page.locator('#close-import').click();
    // Seed only fictional data through the actual import endpoint for visual QA.
    const sample = await send({ method: 'GET', path: '/api/sample' });
    await send({ method: 'POST', path: '/api/import', body: sample.body });
    await page.locator('#refresh-button').click();
    await until(async () => (await page.locator('#stat-total').innerText()) === '5', 'sample import');
    const artifacts = path.join(root, 'artifacts');
    await fs.mkdir(artifacts, { recursive: true });
    await page.screenshot({ path: path.join(artifacts, 'desktop.png'), fullPage: true });
    await page.getByRole('button', { name: 'View Alice Chen', exact: true }).click();
    await page.screenshot({ path: path.join(artifacts, 'contact-detail.png'), fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'mobile layout overflows');
    await page.screenshot({ path: path.join(artifacts, 'mobile.png'), fullPage: true });
    // Ensure user strings cannot become executable HTML.
    const xss = await send({ method: 'POST', path: '/api/contacts', headers: { 'content-type': 'application/json' }, body: Buffer.from(JSON.stringify({ name: '<img src=x onerror=alert(1)>', methods: [] })).toString('base64') });
    assert.equal(xss.status, 201);
    await page.locator('#refresh-button').click();
    await until(async () => (await page.locator('#stat-total').innerText()) === '6', 'safe text render');
    assert.equal(await page.locator('.contact-row img').count(), 0);
    assert.deepEqual(errors, []);
    console.log('PASS: create/edit/delete, multiple methods, persistence, bookmarks, search, XLSX export/import, duplicate skip, desktop/mobile and safe rendering.');
  } finally {
    if (browser) await browser.close();
    bridge.stdin.end();
    bridge.kill();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
