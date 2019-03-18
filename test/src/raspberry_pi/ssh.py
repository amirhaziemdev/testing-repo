import paramiko
import time

class ssh_con():
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect("192.168.1.225", username="pi", password="txmr1234")

    def commands(self, str):
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(str)
    
x = ssh_con()    
x.commands("python Documents/gpio_test.py --d 'f'")
print("test1")
# print(time.time())
time.sleep(20)
# # commands("python Documents/gpio_test.py --d 'b'")
# # print("test2")
# # time.sleep(10)
x.commands("exit()")
print("test3")
# print(time.time())