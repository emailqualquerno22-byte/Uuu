const { chromium } = require('playwright');

(async () => {
  const token = 'zNo0j6N3ep5WW3pmdJLuRn8PC7qPbphvW_A1hFtM8lc';
  const hiveApiKey = '6Z7/ZOYoT3O3CNwGSF4DOA==';
  const hiveBaseUrl = 'https://api-cdn.thehive.ai/api/v3';
  const hiveModel = 'deepseek-ai/deepseek-v4.1-flash-1017';

  console.log('=== INICIANDO TESTE DO DEEPSEEK HARNESS COM CHAVE HIVE ===');
  console.log(`Token: ${token}`);
  console.log(`Hive Base URL: ${hiveBaseUrl}`);
  console.log(`Hive Model: ${hiveModel}`);

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-seccomp-filter-sandbox', '--ignore-certificate-errors']
  });

  const context = await browser.newContext({
    ignoreHTTPSErrors: true
  });

  const page = await context.newPage();

  // Capturar logs de console
  page.on('console', msg => console.log('[PAGE CONSOLE]', msg.text()));
  page.on('pageerror', err => console.log('[PAGE ERROR]', err.message));

  try {
    // 1. Acessar a URL com token
    const url = `http://127.0.0.1:3080/?token=${token}`;
    console.log(`\n[1] Acessando: ${url}`);
    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.log(`    Status: ${response.status()}`);
    console.log(`    URL final: ${page.url()}`);

    // Aguardar a página carregar
    await page.waitForTimeout(3000);

    // 2. Tentar navegar para Settings → Models
    console.log('\n[2] Procurando por Settings/Models...');

    // Tentar clicar em Settings ou navegar diretamente
    // O dsh UI pode ter rotas como /settings ou /models
    try {
      await page.goto('http://127.0.0.1:3080/settings', { waitUntil: 'domcontentloaded', timeout: 15000 });
      console.log('    Navegou para /settings');
    } catch (e) {
      console.log('    /settings não acessível diretamente:', e.message);
    }

    await page.waitForTimeout(2000);

    // 3. Verificar o conteúdo da página
    const pageContent = await page.content();
    console.log(`\n[3] Conteúdo da página (primeiros 500 chars):`);
    console.log(pageContent.substring(0, 500));

    // 4. Tentar encontrar campos de input para API key
    const inputs = await page.$$('input[type="password"], input[type="text"], textarea');
    console.log(`\n[4] Campos de input encontrados: ${inputs.length}`);
    for (let i = 0; i < Math.min(inputs.length, 10); i++) {
      const placeholder = await inputs[i].getAttribute('placeholder') || '';
      const name = await inputs[i].getAttribute('name') || '';
      const id = await inputs[i].getAttribute('id') || '';
      console.log(`    Input ${i}: placeholder="${placeholder}" name="${name}" id="${id}"`);
    }

    // 5. Tentar preencher a chave da Hive se encontrar campo relevante
    for (let i = 0; i < inputs.length; i++) {
      const placeholder = (await inputs[i].getAttribute('placeholder') || '').toLowerCase();
      const name = (await inputs[i].getAttribute('name') || '').toLowerCase();
      if (placeholder.includes('key') || placeholder.includes('api') || name.includes('key') || name.includes('api')) {
        console.log(`\n[5] Preenchendo campo ${i} com a chave da Hive...`);
        await inputs[i].fill(hiveApiKey);
        console.log(`    Chave preenchida`);
        break;
      }
    }

    // 6. Tirar screenshot para evidência
    await page.screenshot({ path: '/tmp/dsh-ui-screenshot.png', fullPage: true });
    console.log('\n[6] Screenshot salvo em /tmp/dsh-ui-screenshot.png');

    // 7. Tentar acessar modelos
    console.log('\n[7] Verificando se há modelos configurados...');
    const modelSelects = await page.$$('select, [role="combobox"], .model-select');
    console.log(`    Seletores de modelo encontrados: ${modelSelects.length}`);

  } catch (err) {
    console.error('\n[ERRO]', err.message);
  } finally {
    await browser.close();
    console.log('\n=== TESTE CONCLUÍDO ===');
  }
})();