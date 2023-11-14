"""
This python application provides a GUI application for configuring settings for
launching ArduPilot SITL simulations. It allows users to select from a list of
aircraft, locations, and adjust weather conditions as needed. The program will
automatically launch RealFlight with those settings, and launch/connect an
ArduPilot SITL instance.

This application also provides the option to introduce random failures to train
operators for emergency procedures.
"""
import os
import tkinter as tk
from tkinter import ttk
import configparser
from collections import OrderedDict
import subprocess
import threading
from modules import realflight

print('Starting SITL Launcher...')

class App(tk.Tk):
    """
    This class creates the application window and contains the event handlers
    for the widgets.
    """
    def __init__(self):
        super().__init__()

        # Create the root window
        self.title('SITL Launcher')

        # Load options in config.ini
        self.config = configparser.ConfigParser(dict_type=OrderedDict)
        self.config.read('config\config.ini')

        self.aircraft_list = []
        self.aircraft_keys = {} # Maps aircraft name to key for folder names
        self.versions = {}
        self.airport_list = []
        self.locations = {}
        # Loop through config and fill the aircraft and airport information
        for category in self.config:
            item = self.config[category]
            if 'type' in item and item['type'] == 'aircraft':
                self.aircraft_list.append(item['name'])
                if item['name'] in self.aircraft_keys:
                    raise Exception('Duplicate aircraft name: {}'.format(item['name']))
                self.aircraft_keys[item['name']] = category
                self.versions[item['name']] = ''.join(
                    item['versions'].split()).split(',')
            if 'type' in item and item['type'] == 'airport':
                self.airport_list.append(item['name'])
                self.locations[item['name']] = item['location']

        # Sort the lists alphabetically
        self.aircraft_list.sort()
        self.airport_list.sort()

        # Create a dictionary to hold the selected options
        self.selected = self.config['selected']

        # Create the widgets
        self.create_widgets()

        # Bind close handler
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        # Prevent resizing
        self.resizable(False, False)

        # Flag to indicate if we have launched headless
        self.headless = False

        # Create member to hold ArduPilot subprocess
        self.ardupilot_process = None
        self.ardupilot_thread = None

        # Start the event loop
        self.mainloop()

    def aircraft_selected(self, _):
        """Update the version combobox when the aircraft is changed"""
        # Get the selected aircraft and version
        self.selected['aircraft'] = self.aircraft_cmb.get()

        # Update the version combobox to the new list
        self.version_cmb['values'] = self.versions[self.selected['aircraft']]

        # If the selected version is not in the new list, select the first one
        if self.selected['version'] not in self.version_cmb['values']:
            self.selected['version'] = self.version_cmb['values'][0]
        self.version_cmb.set(self.selected['version'])

    def version_selected(self, _):
        """Update selected when the version is changed"""
        self.selected['version'] = self.version_cmb.get()

    def airport_selected(self, _):
        """Update selected when the airport is changed"""
        self.selected['airport'] = self.airport_cmb.get()

    def create_widgets(self):
        """Create the GUI for the application"""
        # Create a frame to pack all controls into
        self.controls_frame = ttk.Frame(self)
        # Create a frame to pack console and scroll bar into
        self.console_frame = ttk.Frame(self)

        # Create three labeled frames, Aircraft, Environment, and Failure
        aircraft_frame = ttk.LabelFrame(self.controls_frame, text='Aircraft')
        environment_frame = ttk.LabelFrame(self.controls_frame, text='Environment')
        failure_frame = ttk.LabelFrame(self.controls_frame, text='Failure')
        # Give the first column in each frame a fixed width
        aircraft_frame.columnconfigure(0, minsize=110)
        environment_frame.columnconfigure(0, minsize=110)
        failure_frame.columnconfigure(0, minsize=110)

        # Aircraft frame
        # Aircraft selection
        aircraft_label = ttk.Label(aircraft_frame, text='Aircraft:')
        self.aircraft_cmb = ttk.Combobox(
            aircraft_frame, values=self.aircraft_list, state='readonly')
        self.aircraft_cmb.set(self.selected['aircraft'])
        self.aircraft_cmb.bind('<<ComboboxSelected>>', self.aircraft_selected)
        # ArduPilot Version selection
        version_label = ttk.Label(aircraft_frame, text='ArduPilot Version:')
        self.version_cmb = ttk.Combobox(
            aircraft_frame,
            values=self.versions[self.selected['aircraft']],
            state='readonly')
        self.version_cmb.set(self.selected['version'])
        self.version_cmb.bind('<<ComboboxSelected>>', self.version_selected)
        # Pack the widgets in the aircraft frame
        aircraft_label.grid(row=0, column=0, sticky='e')
        self.aircraft_cmb.grid(row=0, column=1)
        version_label.grid(row=1, column=0, sticky='e')
        self.version_cmb.grid(row=1, column=1)

        # Environment frame
        # Airport selection
        airport_label = ttk.Label(environment_frame, text='Airport:')
        self.airport_cmb = ttk.Combobox(
            environment_frame, values=self.airport_list, state='readonly')
        self.airport_cmb.set(self.selected['airport'])
        self.airport_cmb.bind('<<ComboboxSelected>>', self.airport_selected)
        # Weather selection

        # Pack the widgets in the environment frame
        airport_label.grid(row=0, column=0, sticky='e')
        self.airport_cmb.grid(row=0, column=1)

        # Create two buttons: Launch Headless and Launch RealFlight
        headless_but = ttk.Button(self.controls_frame, text='Launch Headless')
        realflight_but = ttk.Button(self.controls_frame, text='Launch RealFlight')

        # Create textbox to display console output as read-only
        self.console = tk.Text(self.console_frame, wrap='none', state='disabled')
        # Show both vertical and horizontal scrollbars
        console_scrollx = ttk.Scrollbar(
            self.console_frame, orient='horizontal', command=self.console.xview)
        self.console['xscrollcommand'] = console_scrollx.set
        console_scrolly = ttk.Scrollbar(
            self.console_frame, orient='vertical', command=self.console.yview)
        self.console['yscrollcommand'] = console_scrolly.set
        # Place the console and scrollbars with grid
        self.console.grid(row=0, column=0, columnspan=2, sticky='nsew')
        console_scrolly.grid(row=0, column=2, sticky='ns')
        console_scrollx.grid(row=1, column=0, columnspan=2, sticky='ew')
        # Create two buttons: Stop and Reboot
        stop_but = ttk.Button(self.console_frame, text='Stop')
        reboot_but = ttk.Button(self.console_frame, text='Reboot')
        # Handlers
        stop_but['command'] = self.stop_sitl
        reboot_but['command'] = self.launch_sitl
        # Place them on the bottom of the console frame
        stop_but.grid(row=2, column=0, sticky='sew', ipady=10)
        reboot_but.grid(row=2, column=1, sticky='sew', ipady=10)
        self.console_frame.columnconfigure(0, weight=1)
        self.console_frame.columnconfigure(1, weight=1)

        # Configure the console frame to expand with the window
        self.console_frame.rowconfigure(0, weight=1)
        self.console_frame.columnconfigure(0, weight=1)

        # Pack the frames
        aircraft_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        environment_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        failure_frame.grid(row=2, column=0, columnspan=2, sticky='ew')
        # Pack buttons side by side on bottom
        self.controls_frame.rowconfigure(3, weight=1)
        headless_but.grid(row=3, column=0, sticky='sew')
        realflight_but.grid(row=3, column=1, sticky='sew')

        # Pack the controls frame to display it
        self.controls_frame.pack(side='left', fill='y')
        # self.console_frame.pack(side='left', fill='both', expand=True)

        # Click handlers
        headless_but['command'] = self.launch_headless
        realflight_but['command'] = self.launch_realflight

    def launch_headless(self):
        """Launch SITL headless"""
        # Set headless flag
        self.headless = True
        self.launch_sitl()

    def launch_realflight(self):
        """Launch SITL in RealFlight"""
        # Clear headless flag
        self.headless = False

        self.launch_sitl()

    def launch_sitl(self):
        """Launch SITL"""
        # Switch to console view
        self.enable_console()

        self.kill_sitl()

        # If RealFlight, reset aircraft
        if not self.headless:
            realflight.reset_aircraft()

        self.ardupilot_thread = threading.Thread(target=self.run_sitl)
        self.ardupilot_thread.start()

    def kill_sitl(self):
        """Kill running SITL thread/process"""
        if self.ardupilot_thread is not None:
            if self.ardupilot_process is not None:
                self.ardupilot_process.kill()
            self.ardupilot_thread.join()
            self.ardupilot_thread = None

    def stop_sitl(self):
        """Stop SITL"""
        self.kill_sitl()
        self.enable_control()

    def enable_console(self):
        """Switch to console view"""
        self.controls_frame.pack_forget()
        self.console_frame.pack(side='left', fill='both', expand=True)
        # Allow resizing of the window
        self.resizable(True, True)

    def enable_control(self):
        """Switch to control view"""
        self.console_frame.pack_forget()
        self.controls_frame.pack(side='left', fill='y')
        # Disable resizing of the window
        self.resizable(False, False)

    def run_sitl(self):
        """Run ArduPlane.exe"""
        # Clear console
        self.console['state'] = 'normal'
        self.console.delete('1.0', 'end')
        self.console.insert('end', 'Starting SITL...\n')
        self.console['state'] = 'disabled'

        # Get the name of the ardupilot executable
        exename = 'ArduPlane_' + self.selected['version'] + '.exe'

        # Get the folder name of the working directory: aircraft_version_type
        foldername = self.aircraft_keys[self.selected['aircraft']] + '_'
        foldername += self.selected['version'].lower() + '_'
        foldername += 'hl' if self.headless else 'rf'
        # strip whitespace
        foldername = ''.join(foldername.split())

        # Get the path to the cwd
        cwd = os.path.join('bin', foldername)

        # Construct command
        command = [os.path.join('bin', exename)]
        command += ['--defaults', 'defaults.param']
        command += ['-M', 'quadplane' if self.headless else 'flightaxis']
        # Prevent waiting for GCS connection
        command += ['--uartA', 'tcp:0']
        # get location from selected airport
        command += ['-O', self.locations[self.selected['airport']]]

        self.ardupilot_process = subprocess.Popen(command,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  cwd=cwd)

        # Poll the process for new output until finished
        while True:
            if self.ardupilot_process.poll() is not None:
                return
            next_line = self.ardupilot_process.stdout.readline()
            if next_line:
                self.update_text(next_line.decode('utf-8').strip())

    def update_text(self, line):
        """Update the console textbox with the new line"""
        self.console.config(state='normal')
        self.console.insert('end', line + '\n')
        self.console.see('end')
        self.console.config(state='disabled')

    def on_closing(self):
        """Save the config when the window is closed"""
        # Update the config with the selected options
        self.config['selected'] = self.selected
        # Write the config to file
        with open('config\config.ini', 'w', encoding='UTF-8') as configfile:
            self.config.write(configfile)
        self.destroy()


if __name__ == '__main__':
    App()
