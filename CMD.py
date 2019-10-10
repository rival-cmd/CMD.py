import os, subprocess, sys, shlex, traceback
import tkinter as tk
from threading import Thread, RLock
from tkinter import ttk, filedialog


class StdoutRedirector(object):
    """sys.stdout redirect to widget class.\n
        Pass in the text widget object"""
    def __init__(self, widget):
        self.box = widget

    def write(self, string):
        self.box['state'] = 'normal'
        self.box.insert('end', string)
        self.box.see('end')
        self.box['state'] = 'disabled'

    def flush(self):
        pass



class GUI(Thread):
    def __init__(self):
        super().__init__(target=self.run)
        self.main_window = None



    def run(self):
        self.main_window = CommandWindow(self)
        self.main_window.run()
    


class Window(object):
    """Set Shared Window Variables"""
    def __init__(self, title):
        self.root = tk.Tk()
        self.title = title
        self.root.title(title)
        


class CommandWindow(Window):
    """Main Window"""
    def __init__(self, gui):
        super().__init__('Command')
        self.gui= gui
        self.lock = RLock()
        self.build_window()



    def build_window(self):
        """Build Main Window, Widgets and Event Bindings"""
        self.root.geometry('650x450+300+300')
        self.root.minsize(650, 450)

        #frame config
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        #Header Frame
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.grid(row=0, column=0, pady=1)
        ttk.Label(self.header_frame, text='\nCMD.py\n').grid(row=1, column=0, pady=1)
        

        #User Frame
        self.user_frame = ttk.Frame(self.main_frame)
        self.user_frame.grid(row=2, column=0, pady=7)
        

        ttk.Label(self.user_frame, text='Enter Command:').grid(row=3, column=0, pady=5, sticky='W')
        self.command_box = ttk.Entry(self.user_frame, width = 50)
        self.command_box.grid(row=3, column=0)


        self.commandbutton = ttk.Button(self.user_frame, text='Execute Command', command=self.run_command)
        self.commandbutton.grid(row=3, column=0, pady=5, sticky='E')


        ttk.Label(self.user_frame, text="Select Working Directory:").grid(row=6, column=0, pady=5, sticky='W')
        self.filepathbutton = ttk.Button(self.user_frame, text='Select Directory', command=self.select_path)
        self.filepathbutton.grid(row=6, column=0, sticky='E')
        self.directorypath_box = ttk.Entry(self.user_frame, width= 50)
        self.directorypath_box.grid(row=6, column=0)


        self.output_box = tk.Text(self.user_frame, width=75, height=15, wrap ='word', state='disabled')
        self.output_box.grid(row=8, column=0, pady=5)
        self.output_scroll = ttk.Scrollbar(self.user_frame, orient='vertical' , command=self.output_box.yview)
        self.output_scroll.grid(row=8, column=1, sticky='ns')


        self.clearbutton = ttk.Button(self.user_frame, text='Clear', command=self.clear)
        self.clearbutton.grid(row=9, column=0, pady=5, sticky='W')


        self.copybutton= ttk.Button(self.user_frame, text='Copy Output', command=self.copy)
        self.copybutton.grid(row=9, column=0, pady=5, sticky='E')


    def copy(self):
        self.output_box['state'] = 'normal'
        copytext = self.output_box.get("1.0", 'end-1c')
        self.output_box['state'] = 'disabled'

        self.root.clipboard_clear
        self.root.clipboard_append(copytext)

        print('Contents Copied to Clipboard! \n Only available while app is running!')


    def clear(self):
        self.command_box.delete(0,'end')
        self.directorypath_box.delete(0,'end')
        self.output_box['state'] = 'normal'
        self.output_box.delete('1.0','end')
        self.output_box['state'] = 'disabled'


    def select_path(self):
        directorypath = filedialog.askdirectory()
        self.directorypath_box.delete(0,'end')
        self.directorypath_box.insert(0, directorypath)


    def run(self):
        """Main Class Function"""
        sys.stdout = StdoutRedirector(self.output_box)
        self.root.mainloop()


    def run_command(self):
        """Commandbutton callback function"""
        print('Executing Command....\n')
        command = self.command_box.get().rstrip()
        filepath = self.directorypath_box.get().rstrip()
        
        if filepath =="":
            wd = os.getcwd().encode('unicode_escape').decode()
        else:
            wd = filepath.encode('unicode_escape').decode()
        print(command)
        if command == "":
            print("Empty Command Argument")
        else:
            with self.lock:
                try:
                    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=wd)
                    stdout, stderr = process.communicate()
            
                    if stderr.decode('utf-8') == "":
                        print(stdout.decode('utf-8'))
                except Exception:
                    print('Error with Command')
                    print(traceback.print_exc())









def main():
    server = GUI()
    server.run()

if __name__ == "__main__": main()