<#
vba_run - import VBA modules into a workbook, save it as .xlsm and run its test macros.

    powershell -File vba_run.ps1 book.xlsx -Modules modCalc_x.bas[,...] [-Run Test_A,Test_B] [-Out book.xlsm] [-Force]

Exit codes: 0 every test passed | 1 a test failed | 2 setup error (no Excel, no VBA access, bad path).
Windows + desktop Excel only (COM). Needs "Trust access to the VBA project object model"
(File > Options > Trust Center > Macro Settings), which the user turns on; this script never changes it.
A test is a Sub that raises an error on a mismatch (Err.Raise); Debug.Assert would stop a hidden Excel.
#>
param(
    [Parameter(Mandatory, Position = 0)][string]$Workbook,
    [Parameter(Mandatory)][string[]]$Modules,
    [string[]]$Run = @(),
    [string]$Out,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'

function Fail([string]$msg) { Write-Host "ERROR: $msg"; exit 2 }

$src = (Resolve-Path -LiteralPath $Workbook -ErrorAction SilentlyContinue).Path
if (-not $src) { Fail "workbook not found: $Workbook" }
$bas = foreach ($m in $Modules) {
    $p = (Resolve-Path -LiteralPath $m -ErrorAction SilentlyContinue).Path
    if (-not $p) { Fail "module not found: $m" }
    $p
}
if (-not $Out) { $Out = [IO.Path]::ChangeExtension($src, '.xlsm') }
$Out = [IO.Path]::GetFullPath($Out)
if ((Test-Path -LiteralPath $Out) -and -not $Force) { Fail "$Out exists; pass -Force to overwrite it" }

try { $xl = New-Object -ComObject Excel.Application } catch { Fail "desktop Excel is not installed (COM Excel.Application)" }
$wb = $null
$failed = 0
$code = 0
try {
    $xl.Visible = $false
    $xl.DisplayAlerts = $false
    $xl.EnableEvents = $false          # no Workbook_Open from a workbook we did not write
    $wb = $xl.Workbooks.Open($src)

    try { $components = $wb.VBProject.VBComponents }
    catch { throw "no access to the VBA project - the user must tick 'Trust access to the VBA project object model' in the Trust Center" }
    if ($null -eq $components) { throw "no access to the VBA project - the user must tick 'Trust access to the VBA project object model' in the Trust Center" }

    foreach ($p in $bas) {
        $name = (Select-String -LiteralPath $p -Pattern '^Attribute VB_Name = "([^"]+)"' | Select-Object -First 1).Matches.Groups[1].Value
        if (-not $name) { throw "$p has no 'Attribute VB_Name' line (export it from the VBA editor or add it)" }
        foreach ($c in @($components)) { if ($c.Name -eq $name) { $components.Remove($c) } }   # re-import replaces
        [void]$components.Import($p)
        Write-Host "imported $name"
    }

    $wb.SaveAs($Out, 52)               # 52 = xlOpenXMLWorkbookMacroEnabled
    Write-Host "saved $Out"

    foreach ($t in $Run) {
        try { [void]$xl.Run("'$($wb.Name)'!$t"); Write-Host "PASS $t" }
        catch {
            $failed++
            $e = $_.Exception; while ($e.InnerException) { $e = $e.InnerException }
            Write-Host "FAIL $t - $($e.Message)"
        }
    }
}
catch { Write-Host "ERROR: $($_.Exception.Message)"; $code = 2 }
finally {
    if ($wb) { $wb.Close($false) }
    $xl.Quit()
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($xl)   # otherwise EXCEL.EXE lingers
}
if ($code) { exit $code } elseif ($failed) { exit 1 } else { exit 0 }
