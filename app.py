'''

Adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson

Modified by Rui Santos
Complete project details: https://randomnerdtutorials.com

'''

import RPi.GPIO as io
from flask import Flask, render_template, request
from time import sleep
import os
import json
import subprocess
app = Flask(__name__)

io.setmode(io.BCM)

# Create a dictionary called pins to store the pin number, name, and pin state:
hosts = {
   'pis' : {'pin' : 24, 'state' : 'unk' ,'ini' :'' },
   'pij' : {'pin' : 23, 'state' : 'unk' ,'ini' :'' }
   }


def getRunningDetails(host):
   if hosts[host].get('state') == 'up':
      runon = f"ssh pi@{host} "
      hosts[host]['temp'] = subprocess.check_output(runon + "vcgencmd measure_temp",timeout=3, shell=True).decode('utf-8').replace('\r', '').replace('\n', '')
      cpucommand = "grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}'"
      hosts[host]['cpu'] = subprocess.check_output(runon + cpucommand,timeout=3, shell=True).decode('utf-8').replace('\r', '').replace('\n', '')

def getHostStatus(host):
   status =  'up' if os.system("fping -c1 -t500 " + host) == 0 else 'down'
   hostDict = hosts[host]
   hostDict['state']  = status
   if hostDict['ini'] == status:
      hostDict['ini']  = ''
   if status == 'up' and hostDict['ini']  == '' :
      getRunningDetails(host)
   return status


# Set each pin as an output and make it low:
for host, hostdict in hosts.items():
   pin = hostdict.get('pin')
   io.setup(pin, io.OUT)
   io.output(pin, io.HIGH)
   hostdict['state'] = getHostStatus(host)
   


def pulseit(pin):
    io.output(pin, 0) 
    sleep(1)
    io.output(pin, 1)


def startHost(host):
   hostDict = hosts[host]
   if getHostStatus(host) !='up' :
      hostDict['ini'] = 'up' 
      pulseit(hostDict['pin'])

def shutdownHost(host):
   hostDict = hosts[host]
   if getHostStatus(host) !='down':
      hostDict['ini'] = 'down' 
      cmd = f'ssh pi@{host} sudo shutdown'
      os.system(cmd)



@app.route("/")
def main():
   print(hosts)
   return render_template('main.html', hosts=hosts)


@app.route("/<changeHost>/<action>")
def action(changeHost, action):
   hostDict = hosts[host]
   if action == 'status':
      getHostStatus(changeHost)

   if hostDict['ini'] == ''  :
      if action == 'up':
         startHost(changeHost)
      elif action == 'down':
         shutdownHost(changeHost)

   json.dump(hosts,open("hoststatus.json","w"))
   print(hosts)
   return render_template('main.html', hosts=hosts)


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
