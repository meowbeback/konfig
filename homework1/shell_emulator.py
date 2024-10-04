import os
import sys
import argparse
import tarfile

class ShellEmulator:
    def __init__(self, username, hostname, vfs_path, startup_script):
        self.username = username
        self.hostname = hostname
        self.vfs_path = vfs_path
        self.startup_script = startup_script
        self.current_directory = '/'
        self.virtual_fs = self._extract_vfs()

    def _extract_vfs(self):
        with tarfile.open(self.vfs_path, 'r') as tar:
            tar.extractall(path='/tmp/virtual_fs')
        return '/tmp/virtual_fs'

    def _get_prompt(self):
        return f"{self.username}@{self.hostname}:{self.current_directory}$ "

    def _ls(self):
        try:
            items = os.listdir(os.path.join(self.virtual_fs, self.current_directory.strip('/')))
            return "\n".join(items)
        except FileNotFoundError:
            return "No such directory"

    def _cd(self, dir_name):
        target_path = os.path.join(self.virtual_fs, self.current_directory.strip('/'), dir_name)
        if os.path.isdir(target_path):
            self.current_directory = os.path.join(self.current_directory, dir_name)
        else:
            return "No such directory"

    def _mv(self, src, dest):
        src_path = os.path.join(self.virtual_fs, self.current_directory.strip('/'), src)
        dest_path = os.path.join(self.virtual_fs, self.current_directory.strip('/'), dest)
        if os.path.exists(src_path):
            os.rename(src_path, dest_path)
        else:
            return "File not found"
    def _echo(self,text):
            print(text)
    def _tac(self, filename):
        full_path = os.path.join(self.virtual_fs, self.current_directory.strip('/'), filename)
        if os.path.isfile(full_path):
            with open(full_path, 'r') as file:
                lines = file.readlines()
                return '\n'.join(reversed(lines))
        else:
            return "No such file"

    def _exit(self):
        print("Exiting the shell emulator.")
        sys.exit()

    def _execute_command(self, cmd):
        tokens = cmd.split()
        if not tokens:
            return

        command = tokens[0]
        if command == 'ls':
            return self._ls()
        elif command == 'cd':
            if len(tokens) > 1:
                self._cd(tokens[1])
            else:
                return "cd: missing argument"
        elif command == 'mv':
            if len(tokens) == 3:
                self._mv(tokens[1], tokens[2])
            else:
                return "mv: wrong number of arguments"
        elif command == 'tac':
            if len(tokens) == 2:
                return self._tac(tokens[1])
            else:
                return "tac: missing file operand"
        elif command == 'exit':
            self._exit()
        elif command == 'echo':
            a=""
            for i in range(1,len(tokens)):
                a+=tokens[i]+" "
            return self._echo(a)
        else:
            return f"{command}: command not found"


    def run(self):
        if self.startup_script:
            with open(self.startup_script, 'r') as script:
                for line in script:
                    output = self._execute_command(line.strip())
                    if output:
                        print(output)

        while True:
            try:
                cmd = input(self._get_prompt())
                output = self._execute_command(cmd)
                if output:
                    print(output)
            except EOFError:
                break
            except KeyboardInterrupt:
                break

def main():
    parser = argparse.ArgumentParser(description='Shell Emulator')
    parser.add_argument('username', help='Username for prompt')
    parser.add_argument('hostname', help='Hostname for prompt')
    parser.add_argument('vfs_path', help='Path to virtual file system (tar file)')
    parser.add_argument('startup_script', help='Path to startup script file')

    args = parser.parse_args()

    emulator = ShellEmulator(args.username, args.hostname, args.vfs_path, args.startup_script)
    emulator.run()

if __name__ == '__main__':
    main()
