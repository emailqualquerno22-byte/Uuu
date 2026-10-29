const { chromium } = require('playwright');

(async () => {
  const token = 'zNo0j6N3ep5WW3pmdJLuRn8PC7qPbphvW_A1hFtM8lc';
  const hiveApiKey = '6Z7/ZOYoT3O3CNwGSF4DOA==';
  const hiveBaseUrl = 'https://api-cdn.thehive.ai/api/v3';
  const hiveModel = 'deepseek-ai/deepseek-v4.1-flash-1017';

  console.log('=== TESTE DO DEEPSEEK HARNESS COM CHAVE HIVE (v3 - navegação completa) ===');

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

  try {
    // 1. Acessar a URL com token
    const url = `http://127.0.0.1:3080/?token=${token}`;
    console.log(`\n[1] Acessando: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(5000);

    console.log(`    Título: "${await page.title()}"`);

    // 2. Clicar em "Continue" ou "New Session" para entrar na aplicação
    console.log('\n[2] Tentando iniciar sessão...');

    // Procurar botão "Continue" ou "New Session"
    const continueBtn = await page.locator('button:has-text("Continue")').first();
    const newSessionBtn = await page.locator('button:has-text("New Session")').first();
    const chooseWorkspaceBtn = await page.locator('button:has-text("Choose workspace")').first();

    let enteredApp = false;

    // Tentar clicar em "Continue"
    const continueCount = await continueBtn.count();
    if (continueCount > 0) {
      console.log('    Clicando em "Continue"...');
      await continueBtn.click();
      await page.waitForTimeout(5000);
      enteredApp = true;
    } else {
      const newSessionCount = await newSessionBtn.count();
      if (newSessionCount > 0) {
        console.log('    Clicando em "New Session"...');
        await newSessionBtn.click();
        await page.waitForTimeout(5000);
        enteredApp = true;
      } else {
        const chooseCount = await chooseWorkspaceBtn.count();
        if (chooseCount > 0) {
          console.log('    Clicando em "Choose workspace"...');
          await chooseWorkspaceBtn.click();
          await page.waitForTimeout(5000);
          enteredApp = true;
        }
      }
    }

    if (!enteredApp) {
      console.log('    Nenhum botão encontrado para iniciar sessão');
    }

    console.log(`    URL atual: ${page.url()}`);
    console.log(`    Título: "${await page.title()}"`);

    // 3. Procurar elementos da interface da sessão
    console.log('\n[3] Elementos da interface:');
    const allElements = await page.$$('button, input, textarea, select, [role="button"], [role="textbox"], [role="combobox"]');
    console.log(`    Elementos interativos: ${allElements.length}`);

    for (let i = 0; i < Math.min(allElements.length, 30); i++) {
      const tag = await allElements[i].evaluate(el => el.tagName);
      const type = await allElements[i].getAttribute('type') || '';
      const placeholder = await allElements[i].getAttribute('placeholder') || '';
      const text = (await allElements[i].innerText().catch(() => '')).trim().substring(0, 60);
      console.log(`    [${i}] <${tag}> type="${type}" placeholder="${placeholder}" text="${text}"`);
    }

    // 4. Procurar campos de API key ou configurações
    console.log('\n[4] Procurando campos de configuração...');
    const keySelectors = [
      'input[placeholder*="key" i]',
      'input[name*="key" i]',
      'input[id*="key" i]',
      'input[placeholder*="api" i]',
      'input[name*="api" i]',
      'textarea[placeholder*="key" i]',
      'textarea[name*="key" i]',
      'input[type="password"]'
    ];
    for (const sel of keySelectors) {
      const count = await page.locator(sel).count();
      if (count > 0) {
        console.log(`    Encontrado ${count} elemento(s) com seletor: ${sel}`);
        // Tentar preencher o primeiro
        await page.locator(sel).first().fill(hiveApiKey);
        console.log(`    Chave preenchida em: ${sel}`);
        break;
      }
    }

    // 5. Procurar por botões de configuração/settings
    console.log('\n[5] Procurando configurações...');
    const settingsBtns = await page.$$('button:has-text("Settings" i), button:has-text("Config" i), button:has-text("Model" i), button:has-text("Provider" i)');
    console.log(`    Botões de settings/modelo: ${settingsBtns.length}`);
    for (let i = 0; i < Math.min(settingsBtns.length, 5); i++) {
      const text = (await settingsBtns[i].innerText().catch(() => '')).trim();
      console.log(`    [${i}] "${text}"`);
    }

    // 6. Screenshot
    await page.screenshot({ path: '/tmp/dsh-ui-screenshot-v3.png', fullPage: true });
    console.log('\n[6] Screenshot salvo em /tmp/dsh-ui-screenshot-v3.png');

    // 7. Listar todo o texto visível da página para entender a UI
    console.log('\n[7] Texto visível da página (primeiros 1000 chars):');
    const bodyText = await page.locator('body').innerText().catch(() => 'vazio');
    console.log(bodyText.substring(0, 1000));

  } catch (err) {
    console.error('\n[ERRO]', err.message);
  } finally {
    await browser.close();
    console.log('\n=== TESTE CONCLUÍDO ===');
  }
})();