# Copyright (c) 2015  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function
from random import randint

import myo as libmyo; libmyo.init()
import time
import sys

class Listener(libmyo.device_listener.Feed):
    """
    Listener implementation. Return False from any function to
    stop the Hub.
    """

    def __init__(self):
        super(Listener, self).__init__()
        self.player = None
        self.pose = None
        self.hist = []
        self.changed = False
        self.win = False
        self.tie = False
        self.round_num = 1

    def on_connect(self, myo, timestamp, firmware_version):

        #signal connection
        if not self.player:
            self.player = myo.value;
            if myo.value == self.player:
                notify_connection(myo)
                print("connected player ")

    def on_pose(self, myo, timestamp, pose):

        print(self.round_num)

        #determine pose
        if pose == "fingers_spread":
            pose = "P"
        elif pose == "fist":
            pose = "R"
        elif pose == "wave_in":
            pose = "S"
        else:
            return

        #set pose and update history
        self.pose = pose
        self.hist.append(pose)
        self.changed=True

        #determine winner
        if (self.changed) and self.pose:
            print("player:")
            print(self.pose)
            #reset
            self.changed=False
            self.round_num += 1

            winner = check_win(self.pose, generate_ai())
            if winner == 1 :
                self.win = True
            elif winner == -1:
                self.win = False
            elif winner == 0:
                self.tie = True

            #reset
            self.pose = None

        #signal win/loss
        if myo.value == self.player:
            if self.win:
                win(myo)
                self.win = False
                print("player won")
            else:
                if not self.tie:
                    lose(myo)
                    print("player lost")
            if self.tie:
                tie(myo)
                self.tie = False
                print("tie")

def generate_ai():
    #random
    choices = ["R", "P", "S"]
    rand = randint(0,2)
    print("AI choice:")
    print(choices[rand])
    return choices[rand]

def lose(myo):
    myo.vibrate('long')
    myo.vibrate('long')

def win(myo):
    myo.vibrate('short')
    time.sleep(0.5)
    myo.vibrate('short')
    time.sleep(0.5)
    myo.vibrate('short')
    time.sleep(0.5)
    myo.vibrate('short')
    time.sleep(0.5) 
    myo.vibrate('short')
    time.sleep(0.5)

def tie(myo):
    myo.vibrate('short')

def notify_connection(myo):
    myo.vibrate('short')
    time.sleep(1)
    myo.vibrate('long')
    time.sleep(1)
    myo.vibrate('short')

def tie(myo):
    myo.vibrate('short')

        
def main():
    listener = Listener()
    hub = libmyo.Hub()
    hub.set_locking_policy(libmyo.LockingPolicy.none)
    hub.run(1000, listener)

    try:
        while hub.running:
            pass
    except KeyboardInterrupt:
        print("\nQuitting ...")
    finally:
        print("Shutting down hub...")
        hub.shutdown()

def check_win(p1, p2):
    if p1 == "R":
        if p2 == "R":
            return 0
        elif p2 == "P":
            return -1
        elif p2 == "S":
            return 1
    elif p1 == "P":
        if p2 == "R":
            return 1
        elif p2 == "P":
            return 0
        elif p2 == "S":
            return -1
    elif p1 == "S":
        if p2 == "R":
            return -1
        elif p2 == "P":
            return 1
        elif p2 == "S":
            return 0
        
if __name__ == '__main__':
    main()

