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
        self.player1 = None
        self.player2 = None
        self.p1_pose = None
        self.p2_pose = None
        self.p1_hist = []
        self.p2_hist = []
        self.changed = False
        self.one_win = False
        self.two_win = False
        self.round_num = 1

    def on_connect(self, myo, timestamp, firmware_version):

        #signal connection
        if not self.player1:
            self.player1 = myo.value;
            if myo.value == self.player1:
                notify_connection(myo)
                print("connected player1 ")
        elif not self.player2:
            self.player2 = myo.value;
            if myo.value == self.player2:
                notify_connection(myo)
                print("connected player 2")

    def on_pose(self, myo, timestamp, pose):

        print(self.round_num)

        #determine pose
        self.pose = pose
        if pose == "fingers_spread":
            pose = "P"
        elif pose == "fist":
            pose = "R"
        elif pose == "wave_in":
            pose = "S"
        else:
            return

        #set pose and update history
        if  myo.value == self.player1 and not self.p1_pose:
            self.p1_pose = pose
            self.p1_hist.append(pose)
            self.changed=True

        elif myo.value == self.player2 and not self.p2_pose:
            self.p2_pose = pose
            self.p2_hist.append(pose)
            self.changed=True

        #print
        if (self.changed) and self.p1_pose and self.p2_pose:
            print(self.p1_pose, self.p2_pose)
            #reset
            self.changed=False
            self.round_num += 1

        #determine winner
        if self.p1_pose and self.p2_pose:
            winner = check_win(self.p1_pose, self.p2_pose)
            if winner == 1 :
                self.one_win = True
            elif winner == -1:
                self.two_win = True
            elif winner == 0:
                print("Tie!")

            #reset
            self.p1_pose = None
            self.p2_pose = None

        #signal win/loss
        if myo.value == self.player1:
            if self.one_win:
                win(myo)
                self.one_win = False
                print("player 1 won")
            else:
                lose(myo)
                print("player 1 lost")
        if myo.value == self.player2:
            if self.two_win:
                win(myo)
                self.two_win = False;
                print("player 2 won")
            else:
                lose(myo)
                print("player2 lost")




        

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

