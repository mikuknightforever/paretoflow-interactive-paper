param([int] $Port = 3003)
$ErrorActionPreference = 'Stop'
$paretoArticleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $paretoArticleRoot
. (Join-Path $paretoArticleRoot 'theme\myst-command.ps1')
Initialize-ParetoArticleTheme -ArticleRoot $paretoArticleRoot
Invoke-ParetoMyst -MystArguments @('start', '--port', "$Port")
