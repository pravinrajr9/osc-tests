# SSL based communications for QAET engine testing

import subprocess


# Class to handle ssh/scp to engines, handles password
# This is insecure code, the host, password and command are passed directly to a shell without any sort of vetting.
# This is probably okay as it is a test environment, this code does not go to production.
class SSLComm(object):
    def __init__(self, host, password, user="root"):
        self._user_host = user + "@" + host
        self._password = password
        self._ssl_options = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5"

    # Run an ssh command on the remote host
    # Remove the host from the known_hosts first, otherwise ssh may fail
    def ssh(self, command):
        ssh_command = "sshpass -p " + self._password + " ssh " + self._ssl_options + " " + self._user_host + " " + command
        command_result = subprocess.Popen(ssh_command, shell=True, stdout=subprocess.PIPE)
        return command_result.stdout.read().decode("utf-8")

    # This is untested code, put in for Lee Hinman's future use
    # scp a file to the remote host
    def copy_to(self, source, dest):
        return self.copy(source, self._user_host + ":" + dest)

    # scp a file from the remote host
    def copy_from(self, source, dest):
        return self.copy(self._user_host + ":" + source, dest)

    # Helper function: scp a file. Expects the remote host to already be in the file name.
    # Remote the host from known_hosts first, otherwise scp may fail
    def copy(self, source, dest):
        scp_command = "sshpass -p " + self._password + " scp " + self._ssl_options + " " + source + " " + dest
        command_result = subprocess.Popen(scp_command, shell=True, stdout=subprocess.PIPE)
        return command_result.stdout.read().decode("utf-8")
