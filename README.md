# PowerShell Scheduled Input

Windows 11 PowerShell utility that waits until a specified time, activates a target window, pastes a message or TXT file's contents, and presses Enter.

## Requirements

- Windows 11
- Windows PowerShell 5.1 or PowerShell 7
- The target application must already be open and have a visible window

If the target program is elevated as administrator, run this script elevated too. Windows User Interface Privilege Isolation can block input across privilege levels.

## Examples

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\ScheduledInput.ps1 -At '2026-10-12 21:30' -WindowTitle 'Notepad' -Message '회의 자료를 확인해 주세요.'
```

```powershell
.\ScheduledInput.ps1 -At '2026-10-12 21:30' -ProcessName 'notepad' -TextFile '.\message.txt'
```

Use `-NoEnter` to paste without submitting the text.

The script temporarily uses the Windows clipboard and restores its previous text content when possible. It does not execute the text itself; targeting a shell or terminal may cause that target to interpret the pasted text.

## License

MIT
