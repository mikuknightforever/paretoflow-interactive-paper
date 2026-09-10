$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
& npx --yes mystmd@1.10.1 start --port 3003
exit $LASTEXITCODE
