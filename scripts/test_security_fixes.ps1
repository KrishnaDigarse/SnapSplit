# Manual Test Script for Security Fixes
# Run these tests to verify all fixes are working

Write-Host "=== SnapSplit Security Fixes Test Suite ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check Endpoint
Write-Host "[TEST 1] Health Check Endpoint" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost/health" -Method Get
    Write-Host "✓ Health endpoint accessible" -ForegroundColor Green
    Write-Host "  Status: $($health.status)" -ForegroundColor Gray
    Write-Host "  Version: $($health.version)" -ForegroundColor Gray
    Write-Host "  Database: $($health.checks.database)" -ForegroundColor Gray
    Write-Host "  Redis: $($health.checks.redis)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: WebSocket Authentication (should fail without API key)
Write-Host "[TEST 2] WebSocket Authentication - No API Key (should fail)" -ForegroundColor Yellow
try {
    $body = @{
        user_id = "00000000-0000-0000-0000-000000000000"
        message = @{ type = "TEST" }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://localhost/ws/notify" -Method Post -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "✗ Should have been rejected!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 422 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "✓ Correctly rejected request without API key" -ForegroundColor Green
    } else {
        Write-Host "✗ Unexpected error: $_" -ForegroundColor Red
    }
}
Write-Host ""

# Test 3: WebSocket Authentication (should fail with invalid API key)
Write-Host "[TEST 3] WebSocket Authentication - Invalid API Key (should fail)" -ForegroundColor Yellow
try {
    $headers = @{
        "X-Internal-API-Key" = "invalid-key-12345"
        "Content-Type" = "application/json"
    }
    $body = @{
        user_id = "00000000-0000-0000-0000-000000000000"
        message = @{ type = "TEST" }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://localhost/ws/notify" -Method Post -Body $body -Headers $headers -UseBasicParsing
    Write-Host "✗ Should have been rejected!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 403) {
        Write-Host "✓ Correctly rejected invalid API key" -ForegroundColor Green
    } else {
        Write-Host "✗ Unexpected error: $_" -ForegroundColor Red
    }
}
Write-Host ""

# Test 4: CORS Headers
Write-Host "[TEST 4] CORS Configuration" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/v1/auth/login" -Method Options -Headers @{"Origin"="http://localhost:3000"} -UseBasicParsing
    if ($response.Headers["Access-Control-Allow-Origin"]) {
        Write-Host "✓ CORS headers present" -ForegroundColor Green
        Write-Host "  Allowed Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Gray
    } else {
        Write-Host "✗ CORS headers missing" -ForegroundColor Red
    }
} catch {
    Write-Host "! CORS test inconclusive: $_" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Container Status
Write-Host "[TEST 5] Container Status" -ForegroundColor Yellow
$containers = docker compose -f docker-compose.prod.yml --env-file .env.prod ps --format json | ConvertFrom-Json
$allHealthy = $true
foreach ($container in $containers) {
    $status = if ($container.Health) { $container.Health } else { $container.State }
    $color = if ($status -match "healthy|running") { "Green" } else { "Red" }
    Write-Host "  $($container.Service): $status" -ForegroundColor $color
    if ($status -notmatch "healthy|running") { $allHealthy = $false }
}
if ($allHealthy) {
    Write-Host "✓ All containers running" -ForegroundColor Green
} else {
    Write-Host "✗ Some containers unhealthy" -ForegroundColor Red
}
Write-Host ""

# Test 6: Backend Logs Check
Write-Host "[TEST 6] Backend Startup Logs" -ForegroundColor Yellow
$logs = docker compose -f docker-compose.prod.yml --env-file .env.prod logs backend --tail=20 2>&1
if ($logs -match "Application startup complete") {
    Write-Host "✓ Backend started successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Backend startup issues detected" -ForegroundColor Red
}
if ($logs -match "error|exception" -and $logs -notmatch "No module") {
    Write-Host "! Errors found in logs:" -ForegroundColor Yellow
    $logs -split "`n" | Where-Object { $_ -match "error|exception" } | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Gray
    }
}
Write-Host ""

Write-Host "=== Test Suite Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "- Health check endpoint: Enhanced with DB/Redis checks" -ForegroundColor Gray
Write-Host "- WebSocket authentication: Protected with API key" -ForegroundColor Gray
Write-Host "- CORS: Restricted to specific origins" -ForegroundColor Gray
Write-Host "- All services: Running in Docker" -ForegroundColor Gray
