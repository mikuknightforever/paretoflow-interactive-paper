param([switch] $SiteOnly)
$ErrorActionPreference = 'Stop'
$paretoArticleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $paretoArticleRoot
. (Join-Path $paretoArticleRoot 'theme\myst-command.ps1')
Initialize-ParetoArticleTheme -ArticleRoot $paretoArticleRoot
if ($SiteOnly) {
    Invoke-ParetoMyst -MystArguments @('build', '--site')
} else {
    Invoke-ParetoMyst -MystArguments @('build', '--html')
}
& node (Join-Path $paretoArticleRoot 'theme\patch-article-theme.cjs') --check
if ($LASTEXITCODE -ne 0) { throw 'Article theme changed during the build; do not use this output.' }
