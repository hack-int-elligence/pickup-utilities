from sys import *
from subprocess import *
# I give no namespace shits
import multiprocessing
import threading
import subprocess
import signal
import os
import requests
import json
import urllib2


class ProcessNAS(multiprocessing.Process):
    def __init__(self, name, queue):
        self.name_ = name
        self.status = False
        self.process = None
        self.queue_instance = queue
        super(ProcessNAS, self).__init__(target=self.StartCheck, args=(self.queue_instance,))

    def StartCheck(self, queue):
        # Useful regex expression: 
        # echo show Setup:/Network/BackToMyMac | scutil | sed -n 's/.* : *\(.*\).$/\1/p'

        print "Checking for NAS..."
        stdout.flush()
        # Run the discovery specs
        self.process = Popen(["dns-sd", "-B", "_ssh._tcp", "."], stdout=PIPE)
        f_ssh = None
        while not f_ssh:
            line = self.process.stdout.readline()[:-1]
            # Check if we have a relative netstat id
            ssh_key = None
            slug = str("".join("vpybhq").decode('rot13').decode('unicode-escape'))
            if slug in line:
                arr = line.split(" ")
                for string in arr:
                    if slug in string:
                        ssh_key = string[:-1]
            if ssh_key:
                f_ssh = ssh_key
        print "Key found: %s" % f_ssh
        # Add to the thread queue YES THIS IS THREAD SAFE I PROMISE IT REALLY IS
        # Actually though it is
        self.queue_instance.put([f_ssh])
        print '------ Terminating NAS Search ------'


class ExtractSSHKey(object):
    def __init__(self):
        q = multiprocessing.Queue()
        newCheckNAS = ProcessNAS("Drobo-FS", q)
        newCheckNAS.start()
        self.ssh_key = q.get()[0]
        newCheckNAS.terminate()
        self.full_hostname = None

    def GenerateFullHostname(self):
        print "Generating full hostname..."
        # The os.setsid() is passed in the argument preexec_fn so
        # it's run after the fork() and before  exec() to run the shell.
        hostnameScrape = subprocess.Popen(['whoami'], stdout=subprocess.PIPE, 
                               preexec_fn=os.setsid)
        whoami = hostnameScrape.communicate()[0].strip()
        # os.killpg(pro.pid, signal.SIGTERM)  # Send the signal to all the process group
        identScrape = subprocess.Popen(['scutil', '--get', 'LocalHostName'], stdout=subprocess.PIPE,
                               preexec_fn=os.setsid)
        localhost = identScrape.communicate()[0].strip()
        # Combine
        self.full_hostname = whoami + '@' + localhost + '.' + self.ssh_key
        print "Full hostname:\n%s" % self.full_hostname


class PublicAddressExtract(object):
    def __init__(self):
        self.ip = None
        self.request_slug = requests.get("http://ipecho.net/plain")
        hostnameScrape = subprocess.Popen(['whoami'], stdout=subprocess.PIPE, 
                               preexec_fn=os.setsid)
        self.address_prefix = hostnameScrape.communicate()[0].strip()

    def ParseSlug(self):
        self.ip = self.request_slug.text

    def Get(self):
        return self.ip

    def GetAddressPrefix(self):
        return self.address_prefix


class ExtractMac(object):
    def __init__(self):
        super(ExtractMac, self).__init__()
        self.mac_address = None

    # networksetup -listallhardwareports | grep Ethernet | awk '{print $3}' | egrep -v N/A | head -1
    def get_address(self):
        # Generates a valid mac address
        # execute_array = ["networksetup", " -listallhardwarereports", " | ", 
        # "grep Ethernet", " | ", "awk '{print $3}'", " | ", "egrep -v N/A", " | ", "head -1"]
        macScrape = subprocess.Popen("ifconfig  | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}' | head -1", stdout=subprocess.PIPE, 
                                    shell=True, preexec_fn=os.setsid)
        self.mac_address = macScrape.communicate()[0].strip()
        # cmd = "networksetup -listallhardwareports | grep Ethernet | awk '{print $3}' | egrep -v N/A | head -1"
        # self.mac_address = os.system(cmd)

    def Get(self):
        return self.mac_address


import Tkinter

class Installer(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize_welcome()

        self.grid()


    def initialize_welcome(self):
        self.update_geometry()
        self.welcome_label = Tkinter.Label(self, text="Welcome to the Pickup installer!")
        self.welcome_label.grid(row=0)
        self.thank_label = Tkinter.Label(self, text="Thanks for signing up.")
        self.thank_label.grid(row=1)
        
        self.continue_button = Tkinter.Button(self, text="Continue to Account Creation", command=self.destroy_welcome_init_login)
        self.continue_button.grid(columnspan=2)

    def update_geometry(self):
        # Opening dimensions
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        self.geometry("%dx%d+%d+%d" % (size + (x, y)))


    def destroy_welcome_init_login(self):
        self.welcome_label.destroy()
        self.thank_label.destroy()
        self.continue_button.destroy()
        self.initialize_login()
    
    def initialize_login(self, has_username_error=False, has_password_error=False, is_blank_error=False):
        self.update_geometry()
        self.username_entry = Tkinter.Entry(self)
        # self.username_entry.grid(column=3, row=3)

        self.password_entry = Tkinter.Entry(self, show="*")
        # self.password_entry.grid(column=3, row=6)

        self.label_1 = Tkinter.Label(self, text="Username")
        self.label_2 = Tkinter.Label(self, text="Password")

        self.label_1.grid(row=0)
        self.label_2.grid(row=1)

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        self.logbtn = Tkinter.Button(self, text="Login", command=self.account_make_click)
        self.logbtn.grid(columnspan=2)

        self.cancel_button = Tkinter.Button(self, text="Cancel", command=self.cancel_installation)
        self.cancel_button.grid(columnspan=2)

        # print 'username: ' + str(has_username_error)
        if has_username_error or has_password_error or is_blank_error:
            mesg_disp = ""
            if has_username_error:
                mesg_disp = "Username already in use - try again."
            elif has_password_error:
                mesg_disp = "Password must be longer than 6 characters."
            elif is_blank_error:
                mesg_disp = "Username or password can't be blank."
            self.error_label = Tkinter.Label(self, text=mesg_disp)
            self.error_label.grid(columnspan=2)

    def cancel_installation(self):
        self.quit()
        self.destroy()

    def account_make_click(self):
        # get text box
        username_input = self.username_entry.get()
        password_input = self.password_entry.get()
        # Send data to process and send.
        self.process_login_and_send(username_input, password_input)

    def process_login_and_send(self, username, password):
        if len(username) == 0 or len(password) == 0:
            self.destroy_login_window()
            self.initialize_login(has_username_error=False, has_password_error=False, is_blank_error=True)
            return
        if len(password) < 7:
            print 'we here'
            self.destroy_login_window()
            self.initialize_login(has_username_error=False, has_password_error=True)
            return

        # SSH Username
        get = PublicAddressExtract()
        get.ParseSlug()
        ssh_username = get.GetAddressPrefix()

        # MAC Address
        mac_extraction = ExtractMac()
        mac_extraction.get_address()
        mac_address = mac_extraction.Get()

        # Extract Public Address
        ip_find = PublicAddressExtract()
        ip_find.ParseSlug()
        hostname = ip_find.Get()

        # Execute
        self.send_request(username, password, mac_address, ssh_username, hostname)

    def destroy_login_window(self):
        self.username_entry.destroy()
        self.password_entry.destroy()
        self.label_1.destroy()
        self.label_2.destroy()
        self.logbtn.destroy()
        self.cancel_button.destroy()
        if hasattr(self, 'error_label'):
            self.error_label.destroy()


    def send_request(self, username, password, mac_address, ssh_username, hostname):
        payload = {'username': username, 'password': password, 'ssh_username': ssh_username, 'mac_address': mac_address, 'host': hostname}
        print payload
        r = requests.post('http://pickup.azurewebsites.net/register', payload)
        print str(r) + '   ' + str(r.text) + '   ' + str(r.url)
        if json.loads(r.text).get("data") == u'username already exists':
            # things failed bad
            self.destroy_login_window()
            self.initialize_login(has_username_error=True, has_password_error=False)
        else:
            # account success
            self.destroy_login_window()
            self.initialize_post_login()

    def initialize_post_login(self):
        self.update_geometry()
        self.register_success_label = Tkinter.Label(self, text="You've successfully registered with pickup!")
        self.post_success_label = Tkinter.Label(self, text="What are you waiting for?")

        self.register_success_label.grid(row=0)
        self.post_success_label.grid(row=1)

        self.finish_button = Tkinter.Button(self, text="Finish", command=self.quit_and_destroy)
        self.finish_button.grid(columnspan=2)

    def quit_and_destroy(self):
        self.quit()
        self.destroy()
        return
        
        

# # TKinter GUI creation
app = Installer(None)
app.title('Pickup Installer')
app.mainloop()

