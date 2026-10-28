const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

async function main() {
  const imagesDir = path.resolve(__dirname, '../docs/images');
  if (!fs.existsSync(imagesDir)) {
    fs.mkdirSync(imagesDir, { recursive: true });
  }

  console.log('Running python scripts/eval_case_study_cli.py to get raw terminal output...');
  const pythonExe = 'C:\\Users\\letua\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe';
  const scriptPath = path.resolve(__dirname, '../scripts/eval_case_study_cli.py');
  
  let rawOutput = '';
  try {
    rawOutput = execSync(`& "${pythonExe}" "${scriptPath}"`, {
      shell: 'powershell.exe',
      encoding: 'utf-8'
    });
  } catch (err) {
    console.error('Error executing python script:', err);
    process.exit(1);
  }

  console.log('Python script executed successfully. Parsing ANSI escape codes to styled HTML...');

  function ansiToHtml(text) {
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    html = html
      .replace(/\033\[96m\033\[1m/g, '<span class="text-cyan-bold">')
      .replace(/\033\[92m\033\[1m/g, '<span class="text-green-bold">')
      .replace(/\033\[91m\033\[1m/g, '<span class="text-red-bold">')
      .replace(/\033\[93m\033\[1m/g, '<span class="text-yellow-bold">')
      .replace(/\033\[96m/g, '<span class="text-cyan">')
      .replace(/\033\[92m/g, '<span class="text-green">')
      .replace(/\033\[91m/g, '<span class="text-red">')
      .replace(/\033\[93m/g, '<span class="text-yellow">')
      .replace(/\033\[94m/g, '<span class="text-blue">')
      .replace(/\033\[95m/g, '<span class="text-magenta">')
      .replace(/\033\[1m/g, '<span class="font-bold">')
      .replace(/\033\[2m/g, '<span class="text-dim">')
      .replace(/\033\[0m/g, '</span>');

    return html;
  }

  // Split into sections
  const parts = rawOutput.split(/(?=► \[\d\/\d\])/);
  const banner = parts[0] || '';
  const part1 = parts[1] || '';
  const part2 = parts[2] || '';
  const part3 = parts[3] || '';

  function createTerminalPage(content, title = 'PowerShell - python scripts/eval_case_study_cli.py') {
    return `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>${title}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #080c14;
      display: inline-block;
      padding: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .terminal-window {
      width: 1360px;
      background: #0a0d14;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.75), 0 0 0 1px rgba(255, 255, 255, 0.08);
      font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    }
    .terminal-titlebar {
      height: 40px;
      background: #151922;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      user-select: none;
    }
    .tab-group {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .terminal-tab {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 7px 16px;
      background: #0a0d14;
      border-radius: 6px 6px 0 0;
      color: #e2e8f0;
      font-size: 12.5px;
      font-weight: 500;
    }
    .terminal-icon {
      width: 15px;
      height: 15px;
    }
    .window-controls {
      display: flex;
      gap: 12px;
    }
    .control-btn {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      display: inline-block;
    }
    .btn-close { background: #ff5f56; }
    .btn-minimize { background: #ffbd2e; }
    .btn-maximize { background: #27c93f; }

    .terminal-body {
      padding: 24px 28px;
      color: #cbd5e1;
      font-size: 13.5px;
      line-height: 1.55;
      white-space: pre;
    }
    .prompt-line {
      margin-bottom: 16px;
      color: #94a3b8;
    }
    .prompt-path {
      color: #38bdf8;
      font-weight: 600;
    }
    .prompt-cmd {
      color: #f8fafc;
      font-weight: 600;
    }
    .text-cyan { color: #38bdf8; }
    .text-cyan-bold { color: #38bdf8; font-weight: bold; }
    .text-green { color: #4ade80; }
    .text-green-bold { color: #4ade80; font-weight: bold; }
    .text-red { color: #f87171; }
    .text-red-bold { color: #f87171; font-weight: bold; }
    .text-yellow { color: #facc15; }
    .text-yellow-bold { color: #facc15; font-weight: bold; }
    .text-blue { color: #60a5fa; }
    .text-magenta { color: #c084fc; }
    .text-dim { color: #64748b; }
    .font-bold { font-weight: bold; color: #f8fafc; }
    .cursor {
      display: inline-block;
      width: 8px;
      height: 16px;
      background: #38bdf8;
      vertical-align: middle;
      margin-left: 4px;
    }
  </style>
</head>
<body>
  <div class="terminal-window" id="terminal-capture-area">
    <div class="terminal-titlebar">
      <div class="tab-group">
        <div class="terminal-tab">
          <svg class="terminal-icon" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2">
            <polyline points="4 17 10 11 4 5"></polyline>
            <line x1="12" y1="19" x2="20" y2="19"></line>
          </svg>
          <span>PowerShell 7.4 (x64) - M-CDSS Clinical Benchmark</span>
        </div>
      </div>
      <div class="window-controls">
        <span class="control-btn btn-minimize"></span>
        <span class="control-btn btn-maximize"></span>
        <span class="control-btn btn-close"></span>
      </div>
    </div>
    <div class="terminal-body">
<div class="prompt-line"><span class="prompt-path">PS D:\\CODE\\CÁC VẤN ĐỀ HIỆN ĐẠI\\multimodal-ehr-cdss&gt;</span> <span class="prompt-cmd">python scripts/eval_case_study_cli.py</span></div>
${ansiToHtml(content)}
<div class="prompt-line" style="margin-top: 16px;"><span class="prompt-path">PS D:\\CODE\\CÁC VẤN ĐỀ HIỆN ĐẠI\\multimodal-ehr-cdss&gt;</span> <span class="cursor"></span></div>
    </div>
  </div>
</body>
</html>`;
  }

  console.log('Launching Chrome to render Terminal screenshots...');
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  // 1. FULL TERMINAL SCREENSHOT
  console.log('Capturing Terminal 01: Full Evaluation Run...');
  const fullHtml = createTerminalPage(rawOutput);
  const p1 = path.resolve(__dirname, 'temp_term1.html');
  fs.writeFileSync(p1, fullHtml, 'utf-8');
  let page = await browser.newPage({ viewport: { width: 1450, height: 2100 }, deviceScaleFactor: 2 });
  await page.goto('file:///' + p1.replace(/\\/g, '/'), { waitUntil: 'load' });
  const el1 = await page.$('#terminal-capture-area');
  await el1.screenshot({ path: path.join(imagesDir, 'terminal_01_full_evaluation.png') });
  console.log('-> Captured terminal_01_full_evaluation.png');
  await page.close();
  fs.unlinkSync(p1);

  // 2. BENCHMARK TABLE TERMINAL SCREENSHOT
  console.log('Capturing Terminal 02: Benchmark Table Focus...');
  const benchHtml = createTerminalPage(banner + part1);
  const p2 = path.resolve(__dirname, 'temp_term2.html');
  fs.writeFileSync(p2, benchHtml, 'utf-8');
  page = await browser.newPage({ viewport: { width: 1450, height: 950 }, deviceScaleFactor: 2 });
  await page.goto('file:///' + p2.replace(/\\/g, '/'), { waitUntil: 'load' });
  const el2 = await page.$('#terminal-capture-area');
  await el2.screenshot({ path: path.join(imagesDir, 'terminal_02_benchmark_table.png') });
  console.log('-> Captured terminal_02_benchmark_table.png');
  await page.close();
  fs.unlinkSync(p2);

  // 3. CASE STUDIES TERMINAL SCREENSHOT
  console.log('Capturing Terminal 03: Case Studies & Unimodal Discrepancy Focus...');
  const caseHtml = createTerminalPage(part2 + part3);
  const p3 = path.resolve(__dirname, 'temp_term3.html');
  fs.writeFileSync(p3, caseHtml, 'utf-8');
  page = await browser.newPage({ viewport: { width: 1450, height: 1350 }, deviceScaleFactor: 2 });
  await page.goto('file:///' + p3.replace(/\\/g, '/'), { waitUntil: 'load' });
  const el3 = await page.$('#terminal-capture-area');
  await el3.screenshot({ path: path.join(imagesDir, 'terminal_03_case_studies.png') });
  console.log('-> Captured terminal_03_case_studies.png');
  await page.close();
  fs.unlinkSync(p3);

  await browser.close();
  console.log('ALL TERMINAL SCREENSHOTS GENERATED SUCCESSFULLY!');
}

main().catch(err => {
  console.error('Error during terminal capture:', err);
  process.exit(1);
});
