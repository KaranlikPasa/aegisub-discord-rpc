import os
import subprocess

def create_desktop_shortcut():
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    shortcut_path = os.path.join(desktop, 'Aegisub Discord RPC.lnk')
    project_dir = os.path.dirname(os.path.abspath(__file__))
    target_exe = os.path.join(project_dir, 'dist', 'AegisubDiscordRPC', 'AegisubDiscordRPC.exe')
    icon_path = os.path.join(project_dir, 'assets', 'aegisub_icon_128.ico')

    if not os.path.exists(target_exe):
        target_vbs = os.path.join(project_dir, 'run_silently.vbs')
        vbs_content = f"""
Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{shortcut_path}")
Shortcut.TargetPath = "wscript.exe"
Shortcut.Arguments = \"\"\"{target_vbs}\"\"\"
Shortcut.WorkingDirectory = "{project_dir}"
Shortcut.Description = "Aegisub Discord Rich Presence"
Shortcut.IconLocation = "{icon_path}"
Shortcut.Save
"""
    else:
        vbs_content = f"""
Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{shortcut_path}")
Shortcut.TargetPath = "{target_exe}"
Shortcut.WorkingDirectory = "{os.path.dirname(target_exe)}"
Shortcut.Description = "Aegisub Discord Rich Presence"
Shortcut.IconLocation = "{target_exe}"
Shortcut.Save
"""

    vbs_file = os.path.join(project_dir, 'temp_create_shortcut.vbs')
    with open(vbs_file, 'w', encoding='utf-8') as f:
        f.write(vbs_content)

    subprocess.run(['cscript', '//nologo', vbs_file], check=True)
    if os.path.exists(vbs_file):
        os.remove(vbs_file)
    print("Desktop shortcut successfully updated to EXE:", shortcut_path)

if __name__ == '__main__':
    create_desktop_shortcut()
