import subprocess
import uiautomator2 as u2
from util.logger import Logger

class Adb(object):

    legacy = False
    service = ''
    transID = ''
    tcp = False
    u2device = None

    def init(self):
        """Kills and starts a new ADB server
        """
        self.kill_server()
        return self.start_server() 


    def enable_legacy(self):
        """Method to enable legacy adb usage.
        """
        self.legacy = True
        return

    def start_server(self):
        """
        Starts the ADB server and makes sure the android device (emulator) is attached.

        Returns:
            (boolean): True if everything is ready, False otherwise.
        """
        cmd = ['adb', 'start-server']
        subprocess.call(cmd)
        """ hooking onto here, previous implementation of get-state
         is pointless since the script kills the ADB server in advance,
         now seperately connect via usb or tcp, tcp variable is set by main script"""
        if self.tcp and self.connect_tcp():
            Adb.u2device = u2.connect_adb_wifi(Adb.service)
            return True
        else:
            if self.connect_usb():
                Adb.u2device = u2.connect_usb(Adb.service)
                return True
        return False

    def connect_tcp(self):
        cmd = ['adb', 'connect', self.service]
        response = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8')
        if (response.find('connected') == 0) or (response.find('already') == 0):
            self.assign_serial()
            if (self.transID is not None) and self.transID:
                return True
        return False

    def connect_usb(self):
        self.assign_serial()
        if (self.transID is not None) and self.transID:
            cmd = ['adb', '-t', self.transID, 'wait-for-device']
            Logger.log_msg('Waiting for device [' + self.service + '] to be authorized...')
            subprocess.call(cmd)
            Logger.log_msg('Device [' + self.service + '] authorized and connected.')
            return True
        return False


    @staticmethod
    def kill_server():
        """Kills the ADB server
        """
        if Adb.u2device:
            Adb.u2device.disconnect()
        cmd = ['adb', 'kill-server']
        subprocess.call(cmd)

    @staticmethod
    def exec_out(args):
        """Executes the command via exec-out

        Args:
            args (string): Command to execute.

        Returns:
            tuple: A tuple containing stdoutdata and stderrdata
        """
        cmd = ['adb', '-t', Adb.transID , 'exec-out'] + args.split(' ')
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        return process.communicate()[0]

    @staticmethod
    def shell(args):
        """Executes the command via adb shell

        Args:
            args (string): Command to execute.
        """
        cmd = ['adb', '-t', Adb.transID ,'shell'] + args.split(' ')
        Logger.log_debug(str(cmd))
        subprocess.call(cmd)

    @staticmethod
    def cmd(args):
        """Executes a general command of ADB

        Args:
            args (string): Command to execute.
        """
        cmd = ['adb', '-t', Adb.transID] + args.split(' ')
        Logger.log_debug(str(cmd))
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        return process.communicate()[0]

    @classmethod
    def assign_serial(cls):
        cmd = ['adb', 'devices', '-l']
        response = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8').splitlines()
        cls.sanitize_device_info(response)
        cls.transID = cls.get_serial_trans(cls.service, response)

    @staticmethod
    def sanitize_device_info(string_list):
        for index in range(len(string_list) - 1, -1, -1):
            if 'transport_id:' not in string_list[index]:
                string_list.pop(index)

    @staticmethod
    def get_serial_trans(device, string_list):
        for index in range(len(string_list)):
            if device in string_list[index]:
                return string_list[index][string_list[index].index('transport_id:') + 13:]

    @staticmethod
    def print_adb_version():
        cmd = ['adb', '--version']
        response = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8').splitlines()
        for version in response:
            Logger.log_error(version)
