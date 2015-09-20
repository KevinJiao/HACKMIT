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
import json

import time


class Listener(libmyo.device_listener.Feed):
    """
    Listener implementation. Return False from any function to
    stop the Hub.
    """

    interval = 0.05  # Output only 0.05 seconds

    def __init__(self):
        super(Listener, self).__init__()
        self.orientation = None
        self.pose = libmyo.Pose.rest
        self.emg_enabled = False
        self.locked = False
        self.rssi = None
        self.emg = None
        
        self.last_time = 0
        self.id_p1
        self.id_p2

    def output(self):
        ctime = time.time()
        if (ctime - self.last_time) < self.interval:
            return
        self.last_time = ctime

        parts = []
        if self.orientation:
            for comp in self.orientation:
                parts.append(str(comp).ljust(15))
        parts.append(str(self.pose).ljust(10))
        parts.append('E' if self.emg_enabled else ' ')
        parts.append('L' if self.locked else ' ')
        parts.append(self.rssi or 'NORSSI')
        if self.emg:
            for comp in self.emg:
                parts.append(str(comp).ljust(5))
        print('\r' + ''.join('[{0}]'.format(p) for p in parts), end='')
        sys.stdout.flush()

    def on_connect(self, myo, timestamp, firmware_version):
        myo.vibrate('short')
        myo.vibrate('short')
        myo.request_rssi()
        myo.request_battery_level()
        if not self.id_p1:
            print("connected player1 ")
            self.id_p1 = myo.value;
        elif not self.id_p2:
            print("connected player 2")
            self.id_p2 = myo.value;

    def on_rssi(self, myo, timestamp, rssi):
        self.rssi = rssi

    def on_pose(self, myo, timestamp, pose):
        pass

    def on_orientation_data(self, myo, timestamp, orientation):
        self.orientation = orientation

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        pass

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        pass

    def on_emg_data(self, myo, timestamp, emg):
        self.emg = emg

    def on_unlock(self, myo, timestamp):
        self.locked = False

    def on_lock(self, myo, timestamp):
        self.locked = True

    def on_event(self, kind, event):
        """
        Called before any of the event callbacks.
        """

    def on_event_finished(self, kind, event):
        """
        Called after the respective event callbacks have been
        invoked. This method is *always* triggered, even if one of
        the callbacks requested the stop of the Hub.
        """

    def on_pair(self, myo, timestamp, firmware_version):
        """
        Called when a Myo armband is paired.
        """

    def on_unpair(self, myo, timestamp):
        """
        Called when a Myo armband is unpaired.
        """

    def on_disconnect(self, myo, timestamp):
        """
        Called when a Myo is disconnected.
        """

    def on_arm_sync(self, myo, timestamp, arm, x_direction, rotation,
                    warmup_state):
        """
        Called when a Myo armband and an arm is synced.
        """
    def on_arm_unsync(self, myo, timestamp):
        """
        Called when a Myo armband and an arm is unsynced.
        """

    def on_battery_level_received(self, myo, timestamp, level):
        """
        Called when the requested battery level received.
        """

    def on_warmup_completed(self, myo, timestamp, warmup_result):
        """
        Called when the warmup completed.
        """

class RPSGame(Listener):
    def __init__(self):
        super(RPSGame, self).__init__()
        
        self.listener_changed = False
        
        # countdown, posing, post game, post match, main menu
        self.self.state = 'countdown'
        set_json_var('game_state', 'countdown')
        
        self.player_scores = [0, 0]
        self.player_poses = ['','']
        self.player_history = [[],[]]
        
        self.countdown_timer = 0
        self.countdown_timer_max = 3 # seconds
        self.time_intergame = 2
        
        self.start_new_match()
        
        
    def update(self, elapsed_secs):
        if self.state == 'countdown':      # Countdown
            pass
        elif self.state == 'posing':    # Posing
            if self.both_players_posed():
                self.decide_outcome()    
        elif self.state == 'post game':    # Post Game
            self.update_postgame()
        elif self.state == 'post match':    # Post Match
            self.update_post_match()
        elif self.state == 'main menu':    # Main Menu
            pass


    def on_pose(self, myo, timestamp, pose):
        self.pose = pose
        if pose == "fingers_spread":
            pose = "p"
        elif pose == "fist":
            pose = "r"
        elif pose == "wave_in":
            pose = "s"
        else:
            return

        if  myo.value == self.id_p1 and self.player_poses[0] == '':
            self.player_poses[0] = pose
            self.player_history[0].append(pose)
            self.listener_changed=True
            myo.vibrate('short')

        elif myo.value == self.id_p1 and self.player_poses[1] == '':
            self.p2_pose = pose
            self.player_history[1].append(pose)
            myo.vibrate('short')
            self.listener_changed=True

    def start_new_match(self):
        self.player_scores = [0, 0]
        self.player_poses = ['','']  
        self.start_next_game() 

    def start_next_game(self):
        self.state = 'countdown'
        set_json_var('game_state', 'countdown')
        self.countdown_timer = self.countdown_timer_max
    
    def update_countdown(self, elapsed_secs):
        
        print 'countdown: ' + self.countdown_timer
        
        self.countdown_timer -= elapsed_secs
        if self.countdown_timer <= 0:
            self.state = 'posing'
            set_json_var('game_state', 'posing')
    
    def both_players_posed(self):
        return self.pose_p1 != '' and self.pose_p2 != ''
    
    def decide_outcome(self):
        self.state = 'post game'
        set_json_var('game_state', 'post game')
        
        winner = 0
        if (self.pose_p1 == self.pose_p2) winner = 0
        elif (self.pose_p1 == 'r' and self.pose_p2 == 's') or \
             (self.pose_p1 == 's' and self.pose_p2 == 'p') or \
             (self.pose_p1 == 'p' and self.pose_p2 == 'r')
             # game player 1
             winner = 1
        else:
            # game player 2
            winner = 2              
            
        if winner != 0: give_game(winner)
            
    def give_game(self, player_num):
        
        print 'game player', player_num
        
        # scores
        self.player_scores[player_num-1] += 1
        if self.player_scores[player_num-1] == 3:
            give_match(player_num)
            return
        
        # start post_game
        self.state = 'post game'
        set_json_var('game_state', 'post game')
        self.countdown_timer = self.time_intergame
        
    def give_match(self, player_num):
        print 'match player', player_num
        self.state = 'post match'
        set_json_var('game_state', 'post match')
            
    def update_postgame(self, elapsed_secs):
        
        print 'next game in:', self.countdown_timer
        
        self.countdown_timer -= elapsed_secs
        if self.countdown_timer <= 0:
            start_next_game()
            
    def update_post_match(self):
        # query Json for state change
        if self.get_json_var('game_state') == 'main menu' 
        self.state = 'main menu'
        set_json_var('game_state', 'main menu')
    
    def update_main_menu(self):
        # query Json for state change
        if self.get_json_var('game_state') == 'countdown' 
        self.start_new_match()
            
    def set_json_var(self, id, value):      
        with open('data.json', 'r+') as f:
            data = json.load(f)
            data[id] = value # <--- add `id` value.
            f.seek(0)        # <--- should reset file position to the beginning.
            json.dump(data, f, indent=4)
            
    def get_json_var(self, id):
        with open('data.json', 'r+') as f:
            data = json.load(f)
            return data[id]



def main():
    print("Connecting to Myo ... Use CTRL^C to exit.")
    print("If nothing happens, make sure the Bluetooth adapter is plugged in,")
    print("Myo Connect is running and your Myo is put on.")
    
    #feed = libmyo.device_listener.Feed()
    rps_game = RPSGame()
    hub = libmyo.Hub()
    hub.set_locking_policy(libmyo.LockingPolicy.none)
    hub.run(1000, listener)
    
    start_time = time.time()
    
    # Listen to keyboard interrupts and stop the hub in that case.
    try:
        while hub.running:
            elapsed_secs = time.time() - start_time
            start_time = time.time()
            
            if (rps_game.listener_changed):
                #print(rps_game.p1_pose, rps_game.p2_pose)
                listener.listener_changed=False
            rps_game.update(elapsed_secs)
            

    except KeyboardInterrupt:
        print("\nQuitting ...")
    finally:
        print("Shutting down hub...")
        hub.shutdown()

        
if __name__ == '__main__':
    main()

