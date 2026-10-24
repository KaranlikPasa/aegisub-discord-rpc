Set WshShell = CreateObject("WScript.Shell")
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

args = ""
For i = 0 to WScript.Arguments.Count - 1
    args = args & " " & WScript.Arguments(i)
Next

cmd = "pythonw """ & scriptDir & "\main.py""" & args
WshShell.CurrentDirectory = scriptDir
WshShell.Run cmd, 0, False
