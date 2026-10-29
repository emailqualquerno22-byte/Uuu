const { chromium } = require('playwright');

(async () => {
  const token = 'zNo0j6N3ep5WW3pmdJLuRn8PC7qPbphvW_A1hFtM8lc';
  const hiveApiKey = '6Z7/ZOYoT3O3CNwGSF4DOA==';
  const hiveBaseUrl = 'https://api-cdn.thehive.ai/api/v3';
  const hiveModel = 'deepseek-ai/deepseek-v4.1-flash-1017';

  console.log('=== TESTE DO DEEPSEEK HARNESS COM CHAVE HIVE (v2) ===');
  console.log(`Token: ${token}`);
  console.log(`Hive Base URL: ${hiveBaseUrl}`);
  console.log(`Hive Model: ${hiveModel}`);

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-seccomp-filter-sandbox', '--ignore-certificate-errors', '--disable-gpu', '--disable-dev-shm-usage']
  });

  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  page.on('console', msg => console.log('[PAGE CONSOLE]', msg.text()));
  page.on('pageerror', err => console.log('[PAGE ERROR]', err.message));
  page.on('response', res => {
    if (res.status() >= 400) {
      console.log(`[PAGE RESPONSE] ${res.status()} ${res.url()}`);
    }
  });

  try {
    // 1. Acessar a URL com token
    const url = `http://127.0.0.1:3080/?token=${token}`;
    console.log(`\n[1] Acessando: ${url}`);
    const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    console.log(`    Status inicial: ${response.status()}`);

    // Aguardar mais tempo para o SPA renderizar completamente
    console.log('[2] Aguardando renderização do SPA...');
    await page.waitForTimeout(8000);

    // Verificar conteúdo após espera
    const title = await page.title();
    console.log(`    Título da página: "${title}"`);

    const bodyText = await page.locator('body').innerText().catch(() => 'vazio');
    console.log(`    Texto do body (primeiros 300 chars): "${bodyText.substring(0, 300)}"`);

    const html = await page.content();
    console.log(`    Tamanho do HTML: ${html.length} chars`);

    // 3. Procurar por inputs, botões, links
    console.log('\n[3] Procurando elementos interativos...');
    
    const allInputs = await page.$$('input, textarea, select, button, [role="button"], [role="textbox"]');
    console.log(`    Elementos interativos encontrados: ${allInputs.length}`);

    for (let i = 0; i < Math.min(allInputs.length, 20); i++) {
      const tag = await allInputs[i].evaluate(el => el.tagName);
      const type = await allInputs[i].getAttribute('type') || '';
      const placeholder = await allInputs[i].getAttribute('placeholder') || '';
      const name = await allInputs[i].getAttribute('name') || '';
      const id = await allInputs[i].getAttribute('id') || '';
      const text = (await allInputs[i].innerText().catch(() => '')).trim().substring(0, 50);
      console.log(`    [${i}] <${tag}> type="${type}" placeholder="${placeholder}" name="${name}" id="${id}" text="${text}"`);
    }

    // 4. Tentar navegar para rotas específicas
    console.log('\n[4] Tentando navegar para /settings...');
    try {
      await page.goto('http://127.0.0.1:3080/settings', { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(5000);
      const settingsHtml = await page.content();
      console.log(`    HTML de /settings: ${settingsHtml.length} chars`);
      const settingsText = await page.locator('body').innerText().catch(() => 'vazio');
      console.log(`    Texto de /settings: "${settingsText.substring(0, 300)}"`);
    } catch (e) {
      console.log(`    Erro ao acessar /settings: ${e.message}`);
    }

    // 5. Tentar navegar para /models
    console.log('\n[5] Tentando navegar para /models...');
    try {
      await page.goto('http://127.0.0.1:3080/models', { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(5000);
      const modelsHtml = await page.content();
      console.log(`    HTML de /models: ${modelsHtml.length} chars`);
      const modelsText = await page.locator('body').innerText().catch(() => 'vazio');
      console.log(`    Texto de /models: "${modelsText.substring(0, 300)}"`);
    } catch (e) {
      console.log(`    Erro ao acessar /models: ${e.message}`);
    }

    // 6. Se encontrou inputs, tentar preencher
    console.log('\n[6] Procurando campos para preencher a chave...');
    const keyInputs = await page.$$('input[placeholder*="key" i], input[name*="key" i], input[id*="key" i], textarea[placeholder*="key" i], textarea[name*="key" i], textarea[id*="key" i]');
    console.log(`    Campos relacionados a chave: ${keyInputs.length}`);
    if (keyInputs.length > 0) {
      await keyInputs[0].fill(hiveApiKey);
      console.log(`    Chave preenchida no campo [0]`);
    }

    // 7. Screenshot
    await page.screenshot({ path: '/tmp/dsh-ui-screenshot-v2.png', fullPage: true });
    console.log('\n[7] Screenshot salvo em /tmp/dsh-ui-screenshot-v2.png');

    // 8. Listar todos os links na página
    console.log('\n[8] Links encontrados na página:');
    const links = await page.$$('a');
    for (let i = 0; i < Math.min(links.length, 15); i++) {
      const href = await links[i].getAttribute('href') || '';
      const text = (await links[i].innerText().catch(() => '')).trim().substring(0, 40);
      console.log(`    [${i}] href="${href}" text="${text}"`);
    }

  } catch (err) {
    console.error('\n[ERRO]', err.message);
  } finally {
    await browser.close();
    console.log('\n=== TESTE CONCLUÍDO ===');
  }
})();