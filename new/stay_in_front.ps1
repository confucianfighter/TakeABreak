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
    public const int SWP_NOMOVE = 0x0002;
    public const int SWP_NOSIZE = 0x0001;
    public const int SWP_SHOWWINDOW = 0x0040;
}
"@

# Get the handle of the current window
$hwnd = [User32]::GetForegroundWindow()

# Set the window as topmost (always on top)
[User32]::SetWindowPos($hwnd, [User32]::HWND_TOPMOST, 0, 0, 0, 0, [User32]::SWP_NOMOVE -bor [User32]::SWP_NOSIZE -bor [User32]::SWP_SHOWWINDOW)
