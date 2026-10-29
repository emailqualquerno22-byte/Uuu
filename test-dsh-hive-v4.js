const { chromium } = require('playwright');

(async () => {
  const token = 'zNo0j6N3ep5WW3pmdJLuRn8PC7qPbphvW_A1hFtM8lc';
  const hiveApiKey = '6Z7/ZOYoT3O3CNwGSF4DOA==';
  const hiveBaseUrl = 'https://api-cdn.thehive.ai/api/v3';
  const hiveModel = 'deepseek-ai/deepseek-v4.1-flash-1017';

  console.log('=== TESTE DO DEEPSEEK HARNESS COM CHAVE HIVE (v4 - Add API Key) ===');

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

  let dialogOpened = false;

  // Escutar por diálogos/modais
  page.on('dialog', async dialog => {
    console.log(`[DIALOG] ${dialog.type()}: "${dialog.message()}"`);
    await dialog.dismiss();
  });

  try {
    // 1. Acessar a URL com token
    const url = `http://127.0.0.1:3080/?token=${token}`;
    console.log(`\n[1] Acessando: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(5000);

    console.log(`    Título: "${await page.title()}"`);

    // 2. Clicar em "Add API Key"
    console.log('\n[2] Clicando em "Add API Key"...');
    const addApiKeyBtn = page.locator('button:has-text("Add API Key")').first();
    const count = await addApiKeyBtn.count();
    console.log(`    Botões "Add API Key" encontrados: ${count}`);
    if (count > 0) {
      await addApiKeyBtn.click();
      await page.waitForTimeout(5000);
      dialogOpened = true;
      console.log('    Clique realizado');
    }

    // 3. Procurar por campos que apareceram após clicar
    console.log('\n[3] Procurando campos de formulário...');
    const allInputs = await page.$$('input, textarea, select');
    console.log(`    Inputs encontrados: ${allInputs.length}`);
    for (let i = 0; i < Math.min(allInputs.length, 15); i++) {
      const tag = await allInputs[i].evaluate(el => el.tagName);
      const type = await allInputs[i].getAttribute('type') || '';
      const placeholder = await allInputs[i].getAttribute('placeholder') || '';
      const name = await allInputs[i].getAttribute('name') || '';
      const id = await allInputs[i].getAttribute('id') || '';
      console.log(`    [${i}] <${tag}> type="${type}" placeholder="${placeholder}" name="${name}" id="${id}"`);
    }

    // 4. Tentar preencher campo de API key
    console.log('\n[4] Preenchendo campo de API key com a chave da Hive...');
    const keySelectors = [
      'input[placeholder*="key" i]',
      'input[name*="key" i]',
      'input[id*="key" i]',
      'input[type="password"]',
      'textarea[placeholder*="key" i]',
      'input[value=""]'
    ];
    let filled = false;
    for (const sel of keySelectors) {
      try {
        const loc = page.locator(sel).first();
        const cnt = await loc.count();
        if (cnt > 0) {
          await loc.fill(hiveApiKey);
          console.log(`    Chave preenchida em: ${sel}`);
          filled = true;
          break;
        }
      } catch (e) {
        // continuar tentando
      }
    }
    if (!filled) {
      console.log('    Nenhum campo de chave encontrado para preencher');
    }

    // 5. Procurar botões de confirmação/salvar
    console.log('\n[5] Procurando botões de confirmação...');
    const confirmBtns = await page.locator('button:has-text("Salvar" i), button:has-text("Save" i), button:has-text("Confirmar" i), button:has-text("Confirm" i), button:has-text("Adicionar" i), button:has-text("Add" i)');
    const confirmCount = await confirmBtns.count();
    console.log(`    Botões de confirmação: ${confirmCount}`);
    for (let i = 0; i < Math.min(confirmCount, 5); i++) {
      const text = (await confirmBtns.nth(i).innerText().catch(() => '')).trim();
      console.log(`    [${i}] "${text}"`);
    }

    // 6. Screenshot
    await page.screenshot({ path: '/tmp/dsh-ui-screenshot-v4.png', fullPage: true });
    console.log('\n[6] Screenshot salvo em /tmp/dsh-ui-screenshot-v4.png');

    // 7. Texto visível
    console.log('\n[7] Texto visível da página:');
    const bodyText = await page.locator('body').innerText().catch(() => 'vazio');
    console.log(bodyText.substring(0, 1500));

  } catch (err) {
    console.error('\n[ERRO]', err.message);
  } finally {
    await browser.close();
    console.log('\n=== TESTE CONCLUÍDO ===');
  }
})();