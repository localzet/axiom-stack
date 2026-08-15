param(
    [Parameter(Mandatory = $true)][string]$Owner,
    [switch]$Private
)

$repos = @(
    "axiom-stack", "axiom-spec", "axiom-ir", "axiom-solver", "axiom-synth",
    "axiom-verifier", "axiom-runtime", "axiom-capabilities", "axiom-proof",
    "axiom-zk-bridge", "axiom-node", "axiom-kv-lab", "axiom-research"
)

$visibility = if ($Private) { "--private" } else { "--public" }
foreach ($repo in $repos) {
    Push-Location "..\$repo"
    if (-not (Test-Path ".git")) {
        git init -b main
        git add .
        git commit -m "Initial Axiom research prototype"
    }
    gh repo create "$Owner/$repo" $visibility --source . --remote origin --push
    Pop-Location
}
