# PowerShell script to load .env and run Django

# Load .env.development file
if (Test-Path ".env.development") {
    Get-Content ".env.development" | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $varName = $matches[1]
            $varValue = $matches[2]
            [Environment]::SetEnvironmentVariable($varName, $varValue, "Process")
            Write-Host "Set $varName=$varValue"
        }
    }
} else {
    Write-Host "ERROR .env.development file not found"
    exit 1
}

Write-Host "`nStarting Django development server..."
Write-Host "POSTGRES_HOST set to: $env:POSTGRES_HOST"
Write-Host ""

# Run Django
& python manage.py runserver 0.0.0.0:8000