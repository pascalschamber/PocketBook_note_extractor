import os 
import win32com.client

class Device:
    def __init__(self, device_name='PB741'):
        self.device_name = device_name
        self.book_dir = 'Downloads'
        self.note_dir = 'Notes'
        self.is_device_connected = self.check_is_device_connected()
    
    def check_is_device_connected(self):
        strComputer = "." 
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator") 
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2") 
        colItems = objSWbemServices.ExecQuery("Select * from Win32_LogicalDisk") 
        for objItem in colItems: 
            if objItem.VolumeName == self.device_name:
                self.device_path = objItem.name + '\\'
                self.get_device_data()
                return True
        return False

        
    def get_device_data(self):
        self.books = os.path.join(self.device_path, self.book_dir)
        self.notes = os.path.join(self.device_path, self.note_dir)

