# # $env:PYTHONIOENCODING = "utf-8"
# # $mode = Read-Host "single or multi"
# # $taskId = Read-Host "task ID"
# # $task = Read-Host "coding task"

# # New-Item "evaluation-results" -ItemType Directory -Force | Out-Null

# # @($mode, $taskId, $task) |
# #     .\.venv\Scripts\python.exe -u -B src\run_logged.py 2>&1 |
# #     Tee-Object "evaluation-results\$taskId-$mode.txt"



# #     --------------------------



# $utf8 = New-Object System.Text.UTF8Encoding $false
# [Console]::OutputEncoding = $utf8
# $OutputEncoding = $utf8

# $env:PYTHONIOENCODING = "utf-8"
# $env:NO_COLOR = "1"

# $mode = Read-Host "single or multi"
# $taskId = Read-Host "task ID"
# $task = Read-Host "coding task"

# New-Item "evaluation-results" -ItemType Directory -Force | Out-Null

# @($mode, $taskId, $task) |
#     .\.venv\Scripts\python.exe -u -B src\run_logged.py 2>&1 |
#     Tee-Object "evaluation-results\$taskId-$mode.txt"


$utf8 = New-Object System.Text.UTF8Encoding $false
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
$env:PYTHONIOENCODING = "utf-8"
$env:NO_COLOR = "1"

New-Item "evaluation-results" -ItemType Directory -Force | Out-Null

function Invoke-Task($mode, $taskId, $task) {
    Write-Host "`nRunning $taskId - $mode"

    @($mode, $taskId, $task) |
        .\.venv\Scripts\python.exe -u -B src\run_logged.py 2>&1 |
        Tee-Object "evaluation-results\$taskId-$mode.txt"
}

$number = 0

foreach ($task in Get-Content "src\evaluation\tasks.txt") {
    if (!$task.Trim()) { continue }

    $number++
    $taskId = "E{0:D2}" -f $number

      Invoke-Task "single" $taskId $task
    Invoke-Task "multi" $taskId $task
}