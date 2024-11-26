# Define the path to your Python script
$pythonScriptPath = ".\tkinter_version.py"
$projectRoot = "C:\Daylan\terminal_commands\MindfulCoding\TakeABreak\new"
# Infinite loop to relaunch the script
while ($true) {
    Set-Location $projectRoot
    # Launch the Python script
    Write-Host "Launching Python script..."
    python $pythonScriptPath

    # Check the exit status
    $exitCode = $LASTEXITCODE
    Write-Host "Python script exited with code $exitCode."

    # Optional: Add a delay before relaunching (if needed)
    Start-Sleep -Seconds 2

    # Relaunch the script
    Write-Host "Relaunching Python script..."
}
