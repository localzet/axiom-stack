$ErrorActionPreference = "Stop"
$repos = Get-Content (Join-Path $PSScriptRoot "..\REPOSITORIES.txt")
foreach ($repo in $repos) {
    if ([string]::IsNullOrWhiteSpace($repo)) { continue }
    Write-Host "Ready to publish: $repo"
}
Write-Host "Create the GitHub repositories, add remotes, then push each directory independently."
