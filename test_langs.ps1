$JUDGE0 = "http://localhost:2358"

function Test-Lang {
    param($name, $langId, $code, $noMemLimit=$false)
    $body = @{
        source_code = $code
        language_id = $langId
        stdin = ""
        enable_per_process_and_thread_time_limit = $true
        enable_per_process_and_thread_memory_limit = (-not $noMemLimit)
        cpu_time_limit = 10
        wall_time_limit = 15
        memory_limit = 4194304
        max_processes_and_or_threads = 120
    } | ConvertTo-Json -Depth 3
    try {
        $sub = Invoke-RestMethod -Uri "$JUDGE0/submissions" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 15
        Start-Sleep -Seconds 12
        $r = Invoke-RestMethod "$JUDGE0/submissions/$($sub.token)" -TimeoutSec 15
        $out = if ($r.stdout) { $r.stdout.Trim() } else { "" }
        $err = if ($r.compile_output) { $r.compile_output.Trim() } elseif ($r.message) { $r.message } else { "" }
        $display = if ($out) { $out } elseif ($err) { "FAIL: " + $err.Substring(0,[Math]::Min(70,$err.Length)) } else { "(empty)" }
        $icon = if ($r.status.id -eq 3) { "PASS" } else { "FAIL" }
        $time = if ($r.time) { $r.time + "s" } else { "-" }
        $mem  = if ($r.memory) { [math]::Round($r.memory/1024,1).ToString() + "MB" } else { "-" }
        "{0,-12} {1}  {2,-22} {3,-8} {4,-8} {5}" -f $name, $icon, $r.status.description, $time, $mem, $display
    } catch {
        "{0,-12} ERR  {1}" -f $name, $_.Exception.Message.Substring(0,[Math]::Min(60,$_.Exception.Message.Length))
    }
}

Write-Host ""
Write-Host "  CODUKU - Judge0 Language Compatibility Test" -ForegroundColor Cyan
Write-Host "  ============================================" -ForegroundColor DarkGray
Write-Host ("  {0,-12} {1}  {2,-22} {3,-8} {4,-8} {5}" -f "Language","    ","Status","Time","Memory","Output") -ForegroundColor Yellow
Write-Host ("  " + "-" * 85) -ForegroundColor DarkGray

$javaCode = "public class Main {`n    public static void main(String[] args) {`n        System.out.println(`"Hello from Java!`");`n    }`n}"

$tests = @(
    @{ n="Python";     id=71; c="print('Hello from Python!')" }
    @{ n="JavaScript"; id=63; c='console.log("Hello from JavaScript!")' }
    @{ n="Java";       id=62; c=$javaCode }
    @{ n="C";          id=50; c="#include<stdio.h>`nint main(){printf(`"Hello from C!\n`");return 0;}" }
    @{ n="C++";        id=54; c="#include<iostream>`nusing namespace std;`nint main(){cout<<`"Hello from C++!`"<<endl;return 0;}" }
    @{ n="Rust";       id=73; c='fn main(){println!("Hello from Rust!");}' }
    @{ n="Ruby";       id=72; c='puts "Hello from Ruby!"' }
    @{ n="C#";         id=51; c='using System;class P{static void Main(){Console.WriteLine("Hello from C#!");}}' }
    @{ n="TypeScript"; id=74; c='console.log("Hello from TypeScript!")' }
    @{ n="PHP";        id=68; c='<?php echo "Hello from PHP!\n";' }
)

foreach ($t in $tests) {
    $noMem = if ($t.noMem) { $true } else { $false }
    $result = Test-Lang $t.n $t.id ($t.c -replace '`n', "`n") $noMem
    $color = if ($result -match " PASS ") { "Green" } else { "Red" }
    Write-Host "  $result" -ForegroundColor $color
}

Write-Host ""
Write-Host "  Test complete." -ForegroundColor Cyan
