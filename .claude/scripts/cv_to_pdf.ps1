# Export the CV .docx to PDF via Word COM, preserving hyperlinks and bookmarks.
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/scripts/cv_to_pdf.ps1 `
#       -In "F:\...\CV_Academic_Moritz_Seebacher_07_26_English.docx" `
#       -Out "F:\...\CV_Academic_Moritz_Seebacher_07_26_English.pdf"
#
# Paths must be absolute — Word resolves relative paths against its own working
# directory, not the shell's.

param(
    [Parameter(Mandatory = $true)][string]$In,
    [Parameter(Mandatory = $true)][string]$Out
)

if (-not (Test-Path $In)) { Write-Error "Input not found: $In"; exit 1 }

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

try {
    $doc = $word.Documents.Open($In, [ref]$false, [ref]$true)   # no confirm, read-only
    $doc.Repaginate()
    Write-Output ("Pages: " + $doc.ComputeStatistics(2))        # 2 = wdStatisticPages

    # ExportAsFixedFormat: 17 = wdExportFormatPDF, OptimizeForPrint,
    # export the whole document, no markup, embed bookmarks + doc structure tags.
    $doc.ExportAsFixedFormat($Out, 17, $false, 0, 0, 0, 0, 0, $true, $true, 0, $true, $true, $false)

    $doc.Close([ref]$false)
    Write-Output "Exported: $Out"
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
