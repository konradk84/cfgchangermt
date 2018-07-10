import sys, paramiko, re, time, datetime, threading, os, select, configparser

channel_data = bytes()
buf = ''
licznik = int()
prompt = False

cfg = configparser.ConfigParser()
cfg.read('config.ini')

adresy = cfg['DEFAULT']['IP_FILE']
user = cfg['DEFAULT']['LOGIN']
password = cfg['DEFAULT']['PASSWORD']
port = cfg['DEFAULT']['PORT']
cmd = cfg['DEFAULT']['COMMAND']
#to = cfg['DEFAULT]']['TIMEOUT']
timeout = 5

##########################################################################
def file_len(adresy):
    with open(adresy) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
def debug(content):
    print(content)
    czas_teraz = datetime.datetime.now().strftime("%H:%M:%S")
    log_file = open(cfg['DEFAULT']['DEBUG_FILE'], 'a')
    log_buf = ''
    log_buf = 'log: ' +czas_teraz+ ' : '+content + '\n'
    log_file.write(log_buf)
    log_file.close

def log_error(address, content):
    print(address, content)
    czas_teraz = datetime.datetime.now().strftime("%H:%M:%S")
    log_file = open(cfg['DEFAULT']['ERROR_FILE'], 'a')
    log_buf = ''
    log_buf = 'log: ' +czas_teraz+ ' : '+address + ' : '+content + '\n'
    log_file.write(log_buf)
    log_file.close
    
##########################################################################
class run_thread(threading.Thread):
    def __init__(self, wartosc_z, wartosc_w, counter):
        threading.Thread.__init__(self)
        self.wartosc_z = wartosc_z
        self.wartosc_w = wartosc_w
        self.counter = counter
        #self.content = content
    def run(self):
        content = zaloguj_do_mt_rob_telnet(self.wartosc_z, self.wartosc_w)
        #debug("%s zakonczony %s" % (self.counter, result))
        debug(self.counter, self.wartosc_w, content)
############################################################################    
print(adresy)
licznik_adresow = file_len(adresy)
file_in = open(adresy, 'r')
for i, line in enumerate(file_in):
    try:
        licznik = 0
        wyjdz = False
        buf_adr = line
        adr = buf_adr.strip( '\n' )

        debug('############################################\n')
        debug(adr)
        #print('############################################\n')
        print('adres: ', adr)
        
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(adr, port=port, username=user, password=password, timeout=10)
        
        #print("logged in\n")
        debug("logged in\n")
        
        channel = client.invoke_shell()
        channel_data = bytes()
        while wyjdz == False:
            r,w,e = select.select([channel], [], [], timeout)
            if channel in r:
                channel_data += channel.recv(9999)
                buf = channel_data.decode('utf-8')
                print('buf: ', buf)
                if buf.endswith('] > ') == True:
                    debug('jest prompt, wysylamy cmd')
                    channel.send(cmd+'\r\n')
                    channel_data = bytes()
                    channel.send('quit\r\n')
                    continue
                if buf.find('quit\r\n') != -1:
                    debug('odebralismy quit')
                    channel_data = bytes()
                    wyjdz = True
                    break     
        procent = i / licznik_adresow * 100
        print("---------------- wykonano:  ", int(procent), "% -----------------")

    except paramiko.ssh_exception.AuthenticationException as ssherr:
        debug(str(ssherr))
        #print (ssherr)
        client.close()
    except paramiko.ssh_exception.SSHException as ssherr:
        debug(str(ssherr))
        #print (ssherr)
        client.close()
    except paramiko.ssh_exception.socket.error as ssherr:
        debug(str(ssherr))
        #print (ssherr)
        client.close()
    except paramiko.ssh_exception.BadHostKeyException as ssherr:
        debug(str(ssherr))
        #print (ssherr)
        client.close()
    finally:
        client.close()
#print ("done")
debug("done")
	
	
	
	