const { chromium } = require('playwright');

(async () => {
  const token = 'zNo0j6N3ep5WW3pmdJLuRn8PC7qPbphvW_A1hFtM8lc';
  const hiveApiKey = '6Z7/ZOYoT3O3CNwGSF4DOA==';
  const hiveBaseUrl = 'https://api-cdn.thehive.ai/api/v3';
  const hiveModel = 'deepseek-ai/deepseek-v4.1-flash-1017';

  console.log('=== TESTE DO DEEPSEEK HARNESS COM CHAVE HIVE (v5 - salvar e configurar) ===');

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

    // 2. Clicar em "Add API Key"
    console.log('\n[2] Clicando em "Add API Key"...');
    const addApiKeyBtn = page.locator('button:has-text("Add API Key")').first();
    const count = await addApiKeyBtn.count();
    if (count > 0) {
      await addApiKeyBtn.click();
      await page.waitForTimeout(5000);
      console.log('    Clique realizado');
    }

    // 3. Preencher campo de API key
    console.log('\n[3] Preenchendo campo de API key...');
    const pwdInput = page.locator('input[type="password"]').first();
    const pwdCount = await pwdInput.count();
    if (pwdCount > 0) {
      await pwdInput.fill(hiveApiKey);
      console.log('    Chave preenchida no campo de senha');
    }

    // 4. Procurar botão de salvar/adicionar (usando locator com hasText correto)
    console.log('\n[4] Procurando botão de salvar...');
    const saveCandidates = [
      page.locator('button').filter({ hasText: /salvar|save|confirmar|confirm|adicionar|add/i }),
      page.locator('button[type="submit"]'),
      page.locator('button:has-text("Salvar")'),
      page.locator('button:has-text("Save")'),
      page.locator('button:has-text("Add")'),
    ];
    let saveBtn = null;
    for (const cand of saveCandidates) {
      try {
        const cnt = await cand.count();
        if (cnt > 0) {
          saveBtn = cand.first();
          const text = await saveBtn.innerText().catch(() => 'sem texto');
          console.log(`    Botão encontrado: "${text}"`);
          break;
        }
      } catch (e) {
        // continuar
      }
    }

    if (saveBtn) {
      await saveBtn.click();
      await page.waitForTimeout(5000);
      console.log('    Botão de salvar clicado');
    } else {
      console.log('    Nenhum botão de salvar encontrado');
    }

    // 5. Procurar por configurações de modelo/provedor
    console.log('\n[5] Procurando configurações de modelo/provedor...');
    const bodyText = await page.locator('body').innerText().catch(() => 'vazio');
    console.log(`    Texto da página (primeiros 1200 chars):`);
    console.log(bodyText.substring(0, 1200));

    // 6. Procurar botões "New Session" ou similar
    console.log('\n[6] Procurando botão para criar sessão...');
    const sessionBtns = page.locator('button:has-text("New Session"), button:has-text("Nova sessão"), button:has-text("Chat")');
    const sessionCount = await sessionBtns.count();
    console.log(`    Botões de sessão: ${sessionCount}`);
    for (let i = 0; i < Math.min(sessionCount, 5); i++) {
      const text = await sessionBtns.nth(i).innerText().catch(() => '');
      console.log(`    [${i}] "${text.trim()}"`);
    }

    // 7. Screenshot
    await page.screenshot({ path: '/tmp/dsh-ui-screenshot-v5.png', fullPage: true });
    console.log('\n[7] Screenshot salvo em /tmp/dsh-ui-screenshot-v5.png');

  } catch (err) {
    console.error('\n[ERRO]', err.message);
  } finally {
    await browser.close();
    console.log('\n=== TESTE CONCLUÍDO ===');
  }
})();