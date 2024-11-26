using System;
using System.Runtime.InteropServices;

class AlwaysOnTop
{
    // Import the user32.dll SetWindowPos and GetForegroundWindow functions
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    private static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
    private static readonly IntPtr HWND_NOTOPMOST = new IntPtr(-2);
    private const uint SWP_NOMOVE = 0x0002;
    private const uint SWP_NOSIZE = 0x0001;
    private const uint SWP_SHOWWINDOW = 0x0040;

    static void Main(string[] args)
    {
        // Check if the correct argument was provided
        if (args.Length != 1 || (!args[0].Equals("true", StringComparison.OrdinalIgnoreCase) &&
                                  !args[0].Equals("false", StringComparison.OrdinalIgnoreCase)))
        {
            Console.WriteLine("Usage: AlwaysOnTop <true|false>");
            return;
        }

        // Determine whether to set or unset "always on top"
        bool alwaysOnTop = bool.Parse(args[0]);
        IntPtr hWnd = GetForegroundWindow();
        IntPtr hWndInsertAfter = alwaysOnTop ? HWND_TOPMOST : HWND_NOTOPMOST;

        // Set the window position
        if (SetWindowPos(hWnd, hWndInsertAfter, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW))
        {
            Console.WriteLine(alwaysOnTop ? "Window set to always on top." : "Window removed from always on top.");
        }
        else
        {
            Console.WriteLine("Failed to set window position.");
        }
    }
}
