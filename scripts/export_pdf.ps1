$docx = (Resolve-Path "PROJECT_REPORT.docx").Path
$pdf = Join-Path (Get-Location).Path "PROJECT_REPORT.pdf"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docx)
    $doc.SaveAs($pdf, 17)
    $doc.Close()
    Write-Host "PDF generated successfully at: $pdf"
} finally {
    $word.Quit()
}
