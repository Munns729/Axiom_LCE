# Headless API Testing - Quick Start Script
# This script helps you start the services and run tests

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Axiom LCE - Headless API Quick Start                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
$dockerRunning = $false
try {
    docker ps | Out-Null
    $dockerRunning = $true
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running" -ForegroundColor Red
    Write-Host "`nPlease start Docker Desktop and try again." -ForegroundColor Yellow
    Write-Host "After Docker starts, run this script again.`n" -ForegroundColor Yellow
    exit 1
}

# Check if services are already running
Write-Host "`nChecking if services are running..." -ForegroundColor Yellow
$servicesRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -ErrorAction SilentlyContinue
    $servicesRunning = $true
    Write-Host "✓ Services are already running" -ForegroundColor Green
} catch {
    Write-Host "Services are not running yet" -ForegroundColor Yellow
}

if (-not $servicesRunning) {
    Write-Host "`nStarting Docker services..." -ForegroundColor Yellow
    Write-Host "This may take 30-60 seconds...`n" -ForegroundColor Gray
    
    # Start services in background
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; docker compose up" -WindowStyle Normal
    
    Write-Host "Waiting for services to start..." -ForegroundColor Yellow
    $maxWait = 60
    $waited = 0
    $ready = $false
    
    while ($waited -lt $maxWait -and -not $ready) {
        Start-Sleep -Seconds 2
        $waited += 2
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $ready = $true
            }
        } catch {
            Write-Host "." -NoNewline -ForegroundColor Gray
        }
    }
    
    if ($ready) {
        Write-Host "`n✓ Services are ready!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  Services may still be starting..." -ForegroundColor Yellow
        Write-Host "Check the Docker logs in the new window" -ForegroundColor Yellow
    }
}

# Show menu
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Testing Options                           ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Choose a testing approach:`n" -ForegroundColor White

Write-Host "1. Run Python Test Suite (Recommended)" -ForegroundColor Green
Write-Host "   - Tests multiple scenarios automatically" -ForegroundColor Gray
Write-Host "   - Shows detailed results" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Run Original Verification Script" -ForegroundColor Green
Write-Host "   - Simple single test" -ForegroundColor Gray
Write-Host "   - Tests England vs New York mismatch" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Test with PowerShell (Manual)" -ForegroundColor Green
Write-Host "   - Direct API call using Invoke-RestMethod" -ForegroundColor Gray
Write-Host "   - Good for debugging" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Start Word Add-in Server" -ForegroundColor Green
Write-Host "   - Serves the Word Add-in on https://localhost:8080" -ForegroundColor Gray
Write-Host "   - For testing with Microsoft Word" -ForegroundColor Gray
Write-Host ""

Write-Host "5. View Testing Guide" -ForegroundColor Green
Write-Host "   - Opens comprehensive testing documentation" -ForegroundColor Gray
Write-Host ""

Write-Host "Q. Quit" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Enter your choice (1-5 or Q)"

switch ($choice) {
    "1" {
        Write-Host "`nRunning Python Test Suite...`n" -ForegroundColor Cyan
        python test_headless_simple.py
    }
    "2" {
        Write-Host "`nRunning Original Verification Script...`n" -ForegroundColor Cyan
        python verify_headless.py
    }
    "3" {
        Write-Host "`nTesting with PowerShell...`n" -ForegroundColor Cyan
        
        $contractText = "The Governing Law shall be the laws of England."
        $playbook = '{"governing_law": "New York"}'
        
        Write-Host "Contract: $contractText" -ForegroundColor Gray
        Write-Host "Playbook: $playbook" -ForegroundColor Gray
        Write-Host ""
        
        try {
            # Create multipart form data
            $boundary = [System.Guid]::NewGuid().ToString()
            $LF = "`r`n"
            
            $bodyLines = (
                "--$boundary",
                "Content-Disposition: form-data; name=`"file`"; filename=`"test.txt`"",
                "Content-Type: text/plain$LF",
                $contractText,
                "--$boundary",
                "Content-Disposition: form-data; name=`"playbook`"$LF",
                $playbook,
                "--$boundary--$LF"
            ) -join $LF
            
            $response = Invoke-RestMethod -Uri "http://localhost:3000/analyze_logic" `
                -Method Post `
                -ContentType "multipart/form-data; boundary=$boundary" `
                -Body $bodyLines
            
            Write-Host "✓ Success!" -ForegroundColor Green
            Write-Host ($response | ConvertTo-Json -Depth 10)
        } catch {
            Write-Host "✗ Error: $_" -ForegroundColor Red
        }
    }
    "4" {
        Write-Host "`nStarting Word Add-in Server...`n" -ForegroundColor Cyan
        Write-Host "The server will start on https://localhost:8080" -ForegroundColor Yellow
        Write-Host "Press Ctrl+C in the new window to stop it`n" -ForegroundColor Gray
        
        Set-Location "$PSScriptRoot\word-addin"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "npx http-server ./src --ssl --cors -p 8080"
        
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Open https://localhost:8080/taskpane.html in your browser" -ForegroundColor White
        Write-Host "2. Accept the security warning (self-signed certificate)" -ForegroundColor White
        Write-Host "3. Follow the Word Add-in testing guide to sideload the add-in`n" -ForegroundColor White
    }
    "5" {
        Write-Host "`nOpening testing guide...`n" -ForegroundColor Cyan
        $guidePath = "$env:USERPROFILE\.gemini\antigravity\brain\76462d79-603d-4ab7-a8eb-aa6bc27a3a62\headless_api_testing_guide.md"
        if (Test-Path $guidePath) {
            Start-Process $guidePath
        } else {
            Write-Host "Guide not found at: $guidePath" -ForegroundColor Red
        }
    }
    "Q" {
        Write-Host "`nGoodbye!`n" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "`nInvalid choice. Please run the script again.`n" -ForegroundColor Red
    }
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
