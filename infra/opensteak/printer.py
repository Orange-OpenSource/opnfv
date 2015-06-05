#!/usr/bin/python3

import sys


class OpenSteakPrinter:
    """ Just a nice message printer """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def header(self, msg):
        print("""
#
# {}
#
""".format(msg[0:78]))

    def config(self, msg, name, value=None):
        if value is None:
            print(' -', msg, '=', name)
        elif value is False:
            print(' ['+self.FAIL+"KO"+self.ENDC+"]",
                  msg, '>', name, '(NOT found)')
        else:
            print(' ['+self.OKBLUE+"OK"+self.ENDC+"]",
                  msg, '>', name, '=', str(value))

    def list(self, msg):
        print(' -', msg)

    def list_id(self, dic):
        for (k,v) in dic.items():
            self.list("{}: {}".format(k,v))

    def status(self, res, msg, failed="", eol="\n", quit=True):
        if res is True:
            msg = ' ['+self.OKGREEN+"OK"+self.ENDC+"] "+msg
        elif res:
            msg = ' ['+self.OKBLUE+res+self.ENDC+"] "+msg
        else:
            msg = ' ['+self.FAIL+"KO"+self.ENDC+"] "+msg
            if failed:
                msg += ' > '+failed
        msg = msg.ljust(140)+eol
        sys.stdout.write(msg)
        if res is False and quit is True:
            sys.exit(0)

    def ask_validation(self, prompt=None, resp=False, exit=True):
        if prompt is None:
            prompt = 'Continue ?'
        if resp:
            prompt += ' [' + self.BOLD + 'Y' + self.ENDC + '/n]: '
        else:
            prompt += ' [y/' + self.BOLD + 'N' + self.ENDC + ']: '
        while True:
            ans = input(prompt)
            if not ans:
                ans = 'y' if resp else 'n'
            if ans not in ['y', 'Y', 'n', 'N']:
                print('please enter y or n.')
                continue
            if ans == 'y' or ans == 'Y':
                return True
            else:
                if exit:
                    sys.exit(0)
                return False


if __name__ == "__main__":
    p = OpenSteakPrinter()
    import time
    p.config('Var category', 'var1', 'yes, I exist')
    p.config('Var category - bla bla bla bla', 'var2', None)
    p.status(True, "Status message", failed="message if failed")
    p.status('Progress', "Status message - in progress", eol='\r')
    time.sleep(1)
    p.status(True, "Status message", failed="message if failed")
    p.status('Progress', "Status message blah bla", eol='\r')
    time.sleep(1)
    p.status(False, "Status message", failed="message if failed")
    p.status(False, "Status message", failed="message if failed")
