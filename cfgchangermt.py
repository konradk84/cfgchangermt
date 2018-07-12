import sys, paramiko, re, time, datetime, os, select, configparser

channel_data = bytes()
buf = ''
prompt = False

cfg = configparser.ConfigParser()
cfg.read('config.ini')

ip_list = cfg['DEFAULT']['IP_FILE']
user = cfg['DEFAULT']['LOGIN']
password = cfg['DEFAULT']['PASSWORD']
port = cfg['DEFAULT']['PORT']
cmd = cfg['DEFAULT']['COMMAND']
#to = cfg['DEFAULT]']['TIMEOUT']
timeout = 5

##########################################################################
def file_len(ip_list):
    with open(ip_list) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
def debug(content):
    print(content)
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    log_file = open(cfg['DEFAULT']['DEBUG_FILE'], 'a')
    log_buf = ''
    log_buf = 'log: ' +time_now+ ' : '+content + '\n'
    log_file.write(log_buf)
    log_file.close

def log_error(address, content):
    print(address, content)
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    log_file = open(cfg['DEFAULT']['ERROR_FILE'], 'a')
    log_buf = ''
    log_buf = 'log: ' +time_now+ ' : '+address + ' : '+content + '\n'
    log_file.write(log_buf)
    log_file.close

############################################################################    
print(ip_list)
ip_count = file_len(ip_list)
file_in = open(ip_list, 'r')
for i, line in enumerate(file_in):
    try:
        quit_loop = False
        buf_ip = line
        ip = buf_ip.strip( '\n' )

        debug('############################################\n')
        debug(ip)
        #print('############################################\n')
        print('ip_address: ', ip)
        
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port=port, username=user, password=password, timeout=10)
        
        #print("logged in\n")
        debug("logged in\n")
        
        channel = client.invoke_shell()
        channel_data = bytes()
        while quit_loop == False:
            r,w,e = select.select([channel], [], [], timeout)
            if channel in r:
                channel_data += channel.recv(9999)
                buf = channel_data.decode('utf-8')
                print('buf: ', buf)
                if buf.endswith('] > ') == True:
                    debug('We found prompt, sending cmd')
                    channel.send(cmd+'\r\n')
                    channel_data = bytes()
                    channel.send('quit\r\n')
                    continue
                if buf.find('quit\r\n') != -1:
                    debug('Recived quit')
                    channel_data = bytes()
                    quit_loop = True
                    break     
        percent = i / ip_count * 100
        print("---------------- done:  ", int(percent), "% -----------------")

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
	
	
	
	