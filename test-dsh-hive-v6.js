const { chromium } = require('playwright');

(async () => {
  const token = 'zNo0j6N3ep5WW3pmdJLuRn8PC7qPbphvW_A1hFtM8lc';
  const hiveApiKey = '6Z7/ZOYoT3O3CNwGSF4DOA==';
  const hiveBaseUrl = 'https://api-cdn.thehive.ai/api/v3';
  const hiveModel = 'deepseek-ai/deepseek-v4.1-flash-1017';

  console.log('=== TESTE DO DEEPSEEK HARNESS COM CHAVE HIVE (v6 - criar sessão e enviar mensagem) ===');

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

    // 2. Add API Key e salvar (mesmo fluxo que antes)
    console.log('\n[2] Configurando API Key...');
    const addApiKeyBtn = page.locator('button:has-text("Add API Key")').first();
    if (await addApiKeyBtn.count() > 0) {
      await addApiKeyBtn.click();
      await page.waitForTimeout(3000);
      const pwdInput = page.locator('input[type="password"]').first();
      if (await pwdInput.count() > 0) {
        await pwdInput.fill(hiveApiKey);
        console.log('    Chave preenchida');
      }
      const saveBtn = page.locator('button').filter({ hasText: /save and continue/i }).first();
      if (await saveBtn.count() > 0) {
        await saveBtn.click();
        await page.waitForTimeout(5000);
        console.log('    Chave salva');
      }
    }

    // 3. Clicar em "New Session"
    console.log('\n[3] Criando nova sessão...');
    const newSessionBtn = page.locator('button:has-text("New Session")').first();
    if (await newSessionBtn.count() > 0) {
      await newSessionBtn.click();
      await page.waitForTimeout(5000);
      console.log('    Clique em "New Session" realizado');
    }

    console.log(`    URL atual: ${page.url()}`);
    console.log(`    Título: "${await page.title()}"`);

    // 4. Verificar elementos da sessão
    console.log('\n[4] Elementos da interface da sessão:');
    const allElements = await page.$$('button, input, textarea, select, [role="button"], [role="textbox"]');
    console.log(`    Elementos interativos: ${allElements.length}`);
    for (let i = 0; i < Math.min(allElements.length, 25); i++) {
      const tag = await allElements[i].evaluate(el => el.tagName);
      const type = await allElements[i].getAttribute('type') || '';
      const placeholder = await allElements[i].getAttribute('placeholder') || '';
      const text = (await allElements[i].innerText().catch(() => '')).trim().substring(0, 60);
      console.log(`    [${i}] <${tag}> type="${type}" placeholder="${placeholder}" text="${text}"`);
    }

    // 5. Procurar campo de mensagem/input de chat
    console.log('\n[5] Procurando campo de mensagem...');
    const msgSelectors = [
      'textarea[placeholder*="message" i]',
      'textarea[placeholder*="mensagem" i]',
      'textarea[placeholder*="chat" i]',
      'textarea[placeholder*="digite" i]',
      'input[placeholder*="message" i]',
      'input[placeholder*="mensagem" i]',
      'input[type="text"]',
      'div[contenteditable="true"]'
    ];
    let msgField = null;
    for (const sel of msgSelectors) {
      try {
        const loc = page.locator(sel).first();
        const cnt = await loc.count();
        if (cnt > 0) {
          msgField = loc;
          console.log(`    Campo de mensagem encontrado: ${sel}`);
          break;
        }
      } catch (e) {}
    }

    if (msgField) {
      console.log('\n[6] Enviando mensagem de teste...');
      await msgField.fill('Diga apenas: DEEPSEEK HARNESS FUNCIONANDO');
      await page.waitForTimeout(2000);
      console.log('    Mensagem digitada');

      // Procurar botão de enviar
      const sendBtns = page.locator('button:has-text("Enviar" i), button:has-text("Send" i), button:has-text("▶" i)');
      const sendCount = await sendBtns.count();
      console.log(`    Botões de enviar: ${sendCount}`);
      if (sendCount > 0) {
        await sendBtns.first().click();
        await page.waitForTimeout(10000);
        console.log('    Botão de enviar clicado, aguardando resposta...');
      } else {
        // Tentar Enter
        await msgField.press('Enter');
        await page.waitForTimeout(10000);
        console.log('    Enter pressionado, aguardando resposta...');
      }

      // Verificar resposta
      const bodyText = await page.locator('body').innerText().catch(() => 'vazio');
      console.log('\n[7] Resposta recebida (primeiros 1000 chars):');
      console.log(bodyText.substring(0, 1000));
    } else {
      console.log('\n[6] Nenhum campo de mensagem encontrado');
      const bodyText = await page.locator('body').innerText().catch(() => 'vazio');
      console.log(`    Texto da página: ${bodyText.substring(0, 1000)}`);
    }

    // 8. Screenshot
    await page.screenshot({ path: '/tmp/dsh-ui-screenshot-v6.png', fullPage: true });
    console.log('\n[8] Screenshot salvo em /tmp/dsh-ui-screenshot-v6.png');

  } catch (err) {
    console.error('\n[ERRO]', err.message);
  } finally {
    await browser.close();
    console.log('\n=== TESTE CONCLUÍDO ===');
  }
})();