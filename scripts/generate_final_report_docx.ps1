param(
    [string]$OutputPath = "docs\Bao cao M-CDSS - strict split 2026-10-28.docx"
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function XmlEscape([string]$Text) {
    [System.Security.SecurityElement]::Escape($Text)
}

function Run([string]$Text, [bool]$Bold = $false, [int]$Size = 22) {
    $b = if ($Bold) { '<w:b/>' } else { '' }
    "<w:r><w:rPr>$b<w:sz w:val=`"$Size`"/><w:szCs w:val=`"$Size`"/></w:rPr><w:t xml:space=`"preserve`">$(XmlEscape $Text)</w:t></w:r>"
}

function Paragraph([string]$Text, [string]$Style = 'Normal', [bool]$Bold = $false, [int]$Size = 22) {
    "<w:p><w:pPr><w:pStyle w:val=`"$Style`"/></w:pPr>$(Run $Text $Bold $Size)</w:p>"
}

function Table([array]$Rows, [array]$Widths) {
    $grid = ($Widths | ForEach-Object { "<w:gridCol w:w=`"$_`"/>" }) -join ''
    $xml = "<w:tbl><w:tblPr><w:tblW w:w=`"0`" w:type=`"auto`"/><w:tblBorders><w:top w:val=`"single`" w:sz=`"4`"/><w:left w:val=`"single`" w:sz=`"4`"/><w:bottom w:val=`"single`" w:sz=`"4`"/><w:right w:val=`"single`" w:sz=`"4`"/><w:insideH w:val=`"single`" w:sz=`"4`"/><w:insideV w:val=`"single`" w:sz=`"4`"/></w:tblBorders></w:tblPr><w:tblGrid>$grid</w:tblGrid>"
    for ($r = 0; $r -lt $Rows.Count; $r++) {
        $xml += '<w:tr>'
        for ($c = 0; $c -lt $Rows[$r].Count; $c++) {
            $shade = if ($r -eq 0) { '<w:shd w:val="clear" w:fill="D9EAF7"/>' } else { '' }
            $xml += "<w:tc><w:tcPr><w:tcW w:w=`"$($Widths[$c])`" w:type=`"dxa`"/>$shade</w:tcPr><w:p><w:pPr><w:jc w:val=`"center`"/></w:pPr>$(Run ([string]$Rows[$r][$c]) ($r -eq 0) 18)</w:p></w:tc>"
        }
        $xml += '</w:tr>'
    }
    "$xml</w:tbl>"
}

$body = ''
$body += '<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="2200"/></w:pPr>' + (Run 'BÁO CÁO KẾT QUẢ GIAI ĐOẠN 1' $true 36) + '</w:p>'
$body += '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>' + (Run 'HỆ THỐNG M-CDSS' $true 34) + '</w:p>'
$body += '<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="400"/></w:pPr>' + (Run 'Phiên bản strict split — 28/10/2026' $false 22) + '</w:p>'
$body += '<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="400"/></w:pPr>' + (Run 'Dữ liệu tổng hợp và ghi chú lâm sàng đã khử định danh' $false 20) + '</w:p>'
$body += '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

$body += Paragraph 'Tóm tắt điều hành' 'Heading1' $true 28
$body += Paragraph 'Báo cáo này thay thế các số liệu benchmark trước đây. Kiểm tra lại phát hiện nguy cơ rò rỉ dữ liệu do ghi chú hoặc cụm nguồn có thể xuất hiện ở nhiều tập, văn bản chứa tín hiệu quá trực tiếp của nhãn, và một số luật sinh dữ liệu cũ phụ thuộc nhãn. Các kết quả accuracy 94–98% trước đây vì thế không còn là kết luận khoa học chính.'
$body += Paragraph 'Pipeline đã được tái chạy theo chuỗi: khôi phục CSV → converter mới → strict split theo nhóm nguồn → audit → baseline. Trên 302 mẫu kiểm thử độc lập theo nhóm, Bio_ClinicalBERT là baseline tốt nhất; tuy nhiên, đây vẫn chỉ là đánh giá nội bộ trên dữ liệu tổng hợp.'

$body += Paragraph 'Kết quả benchmark' 'Heading1' $true 28
$metricRows = @(
    @('Baseline','AUROC macro','AUPRC macro','F1 macro','Accuracy','Brier','ECE'),
    @('CatBoost (bảng)','0,9223','0,7872','0,6083','0,6854','0,3844','0,0663'),
    @('FT-Transformer (bảng)','0,8976','0,7023','0,5789','0,6589','0,4725','0,1152'),
    @('Bio_ClinicalBERT (văn bản)','0,9735','0,9314','0,8421','0,8543','0,2329','0,0373')
)
$body += Table $metricRows @(2500,1150,1150,1000,1000,850,750)
$body += Paragraph 'Bio_ClinicalBERT đạt AUROC macro 0,9735 và accuracy 0,8543. Với nhánh dữ liệu bảng, CatBoost tốt hơn FT-Transformer. Các chỉ số calibration cần được đọc thận trọng: ECE của BERT là 0,0373, CatBoost là 0,0663 và FT-Transformer là 0,1152.'

$body += Paragraph 'Dữ liệu và strict split' 'Heading1' $true 28
$body += Paragraph 'Nguồn CSV gồm cohort tổng hợp Synthea và MTSamples. Converter mới loại ghi chú trùng giữa nhãn, không quay vòng tái dùng ghi chú, loại transcription/assessment khỏi đầu vào, che tên chẩn đoán đích và lưu source_patient_group/source_note_group để truy vết. Tập raw có 2.000 bản ghi, cân bằng 500 bản ghi mỗi nhãn.'
$splitRows = @(
    @('Tập','Số mẫu','ASTHMA','COPD','HEART_FAILURE','PNEUMONIA'),
    @('Huấn luyện','1.425','358','358','340','369'),
    @('Xác thực','273','71','71','54','77'),
    @('Kiểm thử','302','71','71','106','54')
)
$body += Table $splitRows @(1700,950,1000,900,1600,1250)
$body += Paragraph 'Split sử dụng connected components trên source_patient_group và source_note_group. Audit xác nhận giao nhau train/validation/test bằng 0 theo patient_id, source_patient_group và source_note_group; tất cả split có đủ bốn lớp.'

$body += Paragraph 'Diễn giải và kiểm tra độ tin cậy' 'Heading1' $true 28
$body += Paragraph 'Một sanity check với cây quyết định nông (độ sâu 4) đạt accuracy 0,7285 trên strict test, thấp hơn rõ rệt so với kết quả cũ xấp xỉ 0,955. Sự sụt giảm này phù hợp với nhận định rằng pipeline cũ hưởng lợi từ leakage/lặp nguồn, không phải mô hình mới kém đi.'
$body += Paragraph 'Khoảng chênh validation–test ở FT-Transformer và BERT cho thấy mô hình vẫn nhạy với phân bố nhóm nguồn. Do đó kết quả hiện tại là baseline nội bộ đã được làm sạch, không phải hiệu năng lâm sàng ngoài thực tế.'

$body += Paragraph 'Giới hạn và khuyến nghị' 'Heading1' $true 28
$body += Paragraph 'Dữ liệu tổng hợp và kho công khai không thay thế cohort bệnh viện thực hoặc phản ánh đầy đủ quy trình ghi chép tại Việt Nam. Strict split giảm mạnh leakage theo nguồn nhưng không loại bỏ hoàn toàn domain/style bias. Chưa có bootstrap confidence interval, đánh giá công bằng, hiệu chỉnh ngưỡng theo chi phí lâm sàng hay prospective evaluation.'
$body += Paragraph 'Không sử dụng mô hình để ra quyết định điều trị. Bước tiếp theo: fusion bảng–văn bản với cùng strict split; bootstrap CI và phân tích lỗi theo lớp; leave-source-out/temporal split; sau đó ngoại kiểm dữ liệu thực đã được phê duyệt.'

$body += Paragraph 'Artefact tái lập' 'Heading1' $true 28
$body += Paragraph 'Kết quả: data/rebuilt_strict_results_2026-10-28.json | Audit: data/rebuilt_strict_split_audit.json | ROC/PR: data/rebuilt_strict_curves_2026-10-28.png | Confusion matrix: data/rebuilt_strict_confusion_2026-10-28.png'
$body += Paragraph 'Mã tái lập: scripts/convert_sources_to_raw.py; src/data_pipeline/dataset_loader.py; scripts/audit_data_leakage.py; scripts/run_baselines.py. Hướng dẫn lệnh được cập nhật trong README.md.'

$document = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>$body<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/><w:footerReference w:type="default" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></w:sectPr></w:body></w:document>
"@

$styles = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos" w:cs="Aptos"/></w:rPr></w:rPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:before="360" w:after="160"/><w:keepNext/></w:pPr><w:rPr><w:b/><w:color w:val="1F4E79"/><w:sz w:val="28"/></w:rPr></w:style></w:styles>
"@

$contentTypes = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>
"@
$rootRels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
$docRels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>'
$footer = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:color w:val="777777"/><w:sz w:val="18"/></w:rPr><w:t>M-CDSS — Báo cáo strict split, 28/10/2026</w:t></w:r></w:p></w:ftr>'

$absoluteOutput = Join-Path (Get-Location) $OutputPath
$outDir = Split-Path -Parent $absoluteOutput
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
if (Test-Path -LiteralPath $absoluteOutput) { Remove-Item -LiteralPath $absoluteOutput -Force }
$zip = [System.IO.Compression.ZipFile]::Open($absoluteOutput, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    $files = @{
        '[Content_Types].xml' = $contentTypes
        '_rels/.rels' = $rootRels
        'word/document.xml' = $document
        'word/styles.xml' = $styles
        'word/_rels/document.xml.rels' = $docRels
        'word/footer1.xml' = $footer
    }
    foreach ($name in $files.Keys) {
        $entry = $zip.CreateEntry($name)
        $writer = [System.IO.StreamWriter]::new($entry.Open(), [System.Text.UTF8Encoding]::new($false))
        try { $writer.Write($files[$name]) } finally { $writer.Dispose() }
    }
} finally { $zip.Dispose() }
Write-Output "Created: $absoluteOutput"
