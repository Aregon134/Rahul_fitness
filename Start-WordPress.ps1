$ErrorActionPreference = 'Stop'
$rfProject = $PSScriptRoot
$rfRuntime = Join-Path $rfProject 'runtime\wordpress'
$rfPlugin = Join-Path $rfProject 'wordpress\rahul-fitness-preview'
New-Item -ItemType Directory -Force -Path $rfRuntime | Out-Null
$rfArguments = @('--yes', '@wp-playground/cli@latest', 'server', '--port=9400', '--workers=6', '--wordpress-install-mode=install-from-existing-files-if-needed', '--mount-dir-before-install', $rfRuntime, '/wordpress', '--mount-dir', $rfPlugin, '/wordpress/wp-content/plugins/rahul-fitness-preview', '--login')
if (-not (Test-Path -LiteralPath (Join-Path $rfRuntime '.rahul-preview-ready'))) {
    $rfArguments += @('--blueprint', (Join-Path $rfProject 'local-wordpress.json'))
}
Write-Host 'Rahul Fitness local WordPress preview: http://127.0.0.1:9400/'
Write-Host 'Edit pages: http://127.0.0.1:9400/wp-admin/tools.php?page=rf-preview'
Write-Host 'Press Ctrl+C in this window to stop. Your local edits stay in runtime\wordpress.'
$rfPreload = (Join-Path $rfProject 'localhost-only.cjs').Replace('\', '/')
$rfPriorNodeOptions = $env:NODE_OPTIONS
$env:NODE_OPTIONS = "$rfPriorNodeOptions --require=`"$rfPreload`""
try { & npx.cmd @rfArguments }
finally { $env:NODE_OPTIONS = $rfPriorNodeOptions }
