import os
import pythoncom
import psutil
import win32com.client

class Emulator:
    @classmethod
    def match_list(cls, list1, list2):
        for string in list1:
            cleaned_str = string.strip('"\'')
            if cleaned_str not in list2:
                return False
        return True

    @classmethod
    def extract_command_line_args(cls, emulator_path):
        # Resolve the emulator's actual executable path from a shortcut if provided
        if emulator_path.endswith('.lnk'):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(emulator_path)
            emulator_path = os.path.abspath(shortcut.Targetpath)
            
            # Extract command line arguments from the shortcut
            arguments = shortcut.Arguments
            print(arguments)
            arguments = arguments.split(" ")
            if arguments == [""]:
                arguments = None
        else:
            # No .lnk file, so there are no additional arguments
            arguments = None
        
        return emulator_path, arguments

    @classmethod
    def terminate(cls, emulator_path):
        emulator_path, target_args = cls.extract_command_line_args(emulator_path)
        # Initialize the COM library
        pythoncom.CoInitialize()

        # Iterate over all running processes
        for proc in psutil.process_iter(attrs=['pid', 'name', 'exe', 'cmdline']):
            try:
                process_info = proc.info
                process_exe = process_info.get('exe')  # Use get to handle potential None values

                if process_exe is not None:
                    process_cmdline = process_info.get('cmdline', '')
                    # Compare the executable path and command line arguments
                    if (os.path.normcase(process_exe) == os.path.normcase(emulator_path)):
                        if target_args is None or (process_cmdline and cls.match_list(target_args, process_cmdline)):
                            p = psutil.Process(process_info['pid'])
                            p.terminate()
                            return True  # Emulator process terminated successfully
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return False  # Emulator process not found or termination failed