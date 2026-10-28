const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function main() {
  const imagesDir = path.resolve(__dirname, '../docs/images');
  if (!fs.existsSync(imagesDir)) {
    fs.mkdirSync(imagesDir, { recursive: true });
  }

  console.log('Launching Chrome...');
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 950 },
    deviceScaleFactor: 2
  });

  const page = await context.newPage();

  // 1. ANH 1: Benchmark Metrics Post-Train (/baselines)
  console.log('Capturing Ảnh 1: Benchmark Metrics (/baselines)...');
  await page.goto('http://localhost:3000/baselines', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000); // Allow charts and counters to settle
  await page.screenshot({
    path: path.join(imagesDir, '01_benchmark_metrics_post_train.png'),
    fullPage: false
  });
  console.log('-> Captured 01_benchmark_metrics_post_train.png');

  // Navigate to Intake Form (/)
  console.log('Navigating to Intake Form (/)...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);

  // 2. CASE 1: PT-0044
  console.log('Loading Case 1 (PT-0044)...');
  await page.click('#btn-load-case-1');
  await page.waitForTimeout(1000);

  // Ảnh 2: Case 1 Tabular Data
  const tabularCard1 = await page.$('#tabular-data-card');
  if (tabularCard1) {
    await tabularCard1.screenshot({
      path: path.join(imagesDir, '02_case1_pt0044_tabular_data.png')
    });
    console.log('-> Captured 02_case1_pt0044_tabular_data.png');
  }

  // Ảnh 3: Case 1 Clinical Text
  const clinicalCard1 = await page.$('#clinical-notes-card');
  if (clinicalCard1) {
    await clinicalCard1.screenshot({
      path: path.join(imagesDir, '03_case1_pt0044_clinical_text.png')
    });
    console.log('-> Captured 03_case1_pt0044_clinical_text.png');
  }

  // Ảnh 6: Case 1 Model Predictions
  console.log('Running inference for Case 1...');
  await page.click('#btn-run-inference');
  await page.waitForSelector('#prediction-results-card', { timeout: 10000 });
  await page.waitForTimeout(1500);
  const predictionCard1 = await page.$('#prediction-results-card');
  if (predictionCard1) {
    await predictionCard1.screenshot({
      path: path.join(imagesDir, '06_case1_pt0044_model_predictions.png')
    });
    console.log('-> Captured 06_case1_pt0044_model_predictions.png');
  }

  // 3. CASE 2: PT-0254
  console.log('Loading Case 2 (PT-0254)...');
  await page.click('#btn-load-case-2');
  await page.waitForTimeout(1000);

  // Ảnh 4: Case 2 Tabular Data
  const tabularCard2 = await page.$('#tabular-data-card');
  if (tabularCard2) {
    await tabularCard2.screenshot({
      path: path.join(imagesDir, '04_case2_pt0254_tabular_data.png')
    });
    console.log('-> Captured 04_case2_pt0254_tabular_data.png');
  }

  // Ảnh 5: Case 2 Clinical Text
  const clinicalCard2 = await page.$('#clinical-notes-card');
  if (clinicalCard2) {
    await clinicalCard2.screenshot({
      path: path.join(imagesDir, '05_case2_pt0254_clinical_text.png')
    });
    console.log('-> Captured 05_case2_pt0254_clinical_text.png');
  }

  // Ảnh 7: Case 2 Model Predictions
  console.log('Running inference for Case 2...');
  await page.click('#btn-run-inference');
  await page.waitForSelector('#prediction-results-card', { timeout: 10000 });
  await page.waitForTimeout(1500);
  const predictionCard2 = await page.$('#prediction-results-card');
  if (predictionCard2) {
    await predictionCard2.screenshot({
      path: path.join(imagesDir, '07_case2_pt0254_model_predictions.png')
    });
    console.log('-> Captured 07_case2_pt0254_model_predictions.png');
  }

  await browser.close();
  console.log('All 7 real screenshots captured successfully!');
}

main().catch(err => {
  console.error('Error during capture:', err);
  process.exit(1);
});
