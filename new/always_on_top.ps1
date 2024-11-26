param (
    [bool]$AlwaysOnTop
)
$AlwaysOnTop = [bool]::Parse($AlwaysOnTop)
# Check if the 'User32' type is already defined
if (-not ([System.Management.Automation.PSTypeName]'User32').Type) {
    # Add the necessary type definitions for using Windows API functions
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;

    public class User32 {
        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

        [DllImport("user32.dll", SetLastError = true)]
        public static extern IntPtr GetForegroundWindow();

        public static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
        public static readonly IntPtr HWND_NOTOPMOST = new IntPtr(-2);
        public const int SWP_NOMOVE = 0x0002;
        public const int SWP_NOSIZE = 0x0001;
        public const int SWP_SHOWWINDOW = 0x0040;
    }
"@
}

# Get the handle of the current window
$hwnd = [User32]::GetForegroundWindow()

# Ensure $topmostFlag is correctly set based on $AlwaysOnTop
if ($AlwaysOnTop -eq $true) {
    $topmostFlag = [User32]::HWND_TOPMOST
    Write-Output "Setting window to always on top."
} else {
    $topmostFlag = [User32]::HWND_NOTOPMOST
    Write-Output "Removing always on top setting."
}

# Check that $hwnd and $topmostFlag have valid values before proceeding
if ($hwnd -and $topmostFlag) {
    # Set or unset the "always on top" attribute based on the argument
    [User32]::SetWindowPos($hwnd, $topmostFlag, 0, 0, 0, 0, [User32]::SWP_NOMOVE -bor [User32]::SWP_NOSIZE -bor [User32]::SWP_SHOWWINDOW)
    Write-Output "Window setting updated successfully." 
} else {
    Write-Output "Failed to retrieve window handle or topmost flag."
    Write-Output "Handle: $hwnd"
    Write-Output "Topmost Flag: $topmostFlag"
}
