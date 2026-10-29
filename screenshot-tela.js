const { chromium } = require('playwright');

(async () => {
  const token = 'zNo0j6N3ep5WW3pmdJLuRn8PC7qPbphvW_A1hFtM8lc';

  console.log('=== TIRANDO SCREENSHOT DA TELA ===');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-seccomp-filter-sandbox', '--ignore-certificate-errors', '--disable-gpu', '--disable-dev-shm-usage']
  });

  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1366, height: 768 }
  });

  const page = await context.newPage();

  try {
    // Acessar o DeepSeek Harness
    const url = `http://127.0.0.1:3080/?token=${token}`;
    console.log(`[1] Acessando: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(5000);

    console.log(`    Título: "${await page.title()}"`);
    console.log(`    URL: ${page.url()}`);

    // Tirar screenshot da página completa
    const screenshotPath = '/tmp/tela-container.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`[2] Screenshot salvo em: ${screenshotPath}`);

    // Verificar tamanho do arquivo
    const fs = require('fs');
    const stats = fs.statSync(screenshotPath);
    console.log(`    Tamanho: ${stats.size} bytes`);

  } catch (err) {
    console.error('[ERRO]', err.message);
  } finally {
    await browser.close();
    console.log('=== SCREENSHOT CONCLUÍDO ===');
  }
})();