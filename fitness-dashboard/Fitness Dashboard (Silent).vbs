Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get directory of this script
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' Python interpreter path (use .venv if present, otherwise system python)
If FSO.FileExists(ScriptDir & "\.venv\Scripts\python.exe") Then
    PythonExe = """" & ScriptDir & "\.venv\Scripts\python.exe"""
Else
    PythonExe = "python"
End If

AppScript = ScriptDir & "\app.py"

' Run Streamlit silently (0 = hide window)
Cmd = PythonExe & " -m streamlit run """ & AppScript & """ --server.headless=false --server.port=8501"
WshShell.CurrentDirectory = ScriptDir
WshShell.Run Cmd, 0, False

' Give Streamlit a moment to start and open browser
WScript.Sleep 1500
WshShell.Run "http://localhost:8501", 1, False
