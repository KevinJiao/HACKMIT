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

import sys
import random

pose_human=''
pose_ai=''


class GameInfo(object):
    def __init__(self):
        # poses are  'r', 'p', or 's' ('' means non existing game)
        #pose_ai = ''  
        #pose_human = ''
        
        # outcome is 'w', 'l', 'd' ('' means non existing game)
        self.outcome = '' 
    
    def __str__(self):
        return pose_ai + pose_human + self.outcome
    
class AIPlayer(object):
    
    def __init__(self):
        self.debug = True
        self.greedy_chance = 1
        self.prev_games = []
        self.q_matrix = dict()
        

    def random_pose(self):
        return "rps"[int(random.random() * 3)]
    
    def valid_state(self, state):
        return len(state) == 3 # <ai pose> <human pose> <outcome> <action>
    
    def find_greedy_pose(self, q_matrix, current_state):
        if (not self.valid_state(current_state)) or len(q_matrix) == 0:
            return 0, self.random_pose()
        else:
            # find the best pose with the current state
            max_q = -sys.maxint - 1
            best_pose = self.random_pose()
            
            for i in range(len(self.q_matrix)):
                state = self.q_matrix.keys()[i][0:3]
                
                if state != current_state: continue # only look at q matrix entries with current state
                
                if self.q_matrix.values()[i] > max_q:
                    max_q = self.q_matrix.values()[i]
                    
                    action = self.q_matrix.keys()[i][-1]
                    best_pose = action
                    
            return max_q, best_pose
    
    def get_pose_choice(self):
        
        state = '' if (len(self.prev_games) == 0) else str(self.prev_games[-1])
        pose = ''
        
        q_greedy, pose_greedy = self.find_greedy_pose(self.q_matrix, state)
        
        #if self.debug: print('Q Matrix: ' + self.q_matrix)
        
        if random.random() <= self.greedy_chance and q_greedy > 0:
            # pick greedily
            pose = pose_greedy
            if self.debug: print('picks greedy - q = ' + str(q_greedy))
        else:
            # pick randomly
            pose = self.random_pose()
            if self.debug: print('picks random')
            
        return pose
    
    def update_with_game_outcome(self, pose_ai, pose_human, outcome):
        game = GameInfo()
        game.pose_ai = pose_ai
        game.pose_human = pose_human
        game.outcome = outcome
        
        #-----------------------------------------
        # Update q matrix
        
        state = '' if (len(self.prev_games) == 0) else str(self.prev_games[-1])
        
        if (self.valid_state(state)):            
            state_action_pair = state + game.pose_ai
            
            # create q_matrix entry if not yet existent
            if not state_action_pair in self.q_matrix.keys():
                self.q_matrix[state_action_pair] = 0
                
            # reward for ai pose choice given previous game
            self.q_matrix[state_action_pair] += 1 if game.outcome == 'w' else (-1 if game.outcome == 'l' else 0)
            
            
        # save game to history
        self.prev_games.append(game)


class Listener(libmyo.device_listener.Feed):
    """
    Listener implementation. Return False from any function to
    stop the Hub.
    """

    interval = 0.05  # Output only 0.05 seconds

    def __init__(self):
        super(Listener, self).__init__()
        self.pose = None

        self.myo = None

        self.last_time = 0
        self.id_p1=0
        self.id_p2=0
        #pose_ai = ''
        #pose_human = ''



        self.player_history = [[],[]]

    def on_connect(self, myo, timestamp, firmware_version):
        
        if not self.id_p1:
            print("connected player1 ")
            self.myo = myo
            self.vibrate_notify_connection(myo)
            self.id_p1 = myo.value;

    def on_rssi(self, myo, timestamp, rssi):
        self.rssi = rssi

    def on_pose(self, myo, timestamp, pose):
        global pose_human
        #print(pose)
        self.pose = pose
        if pose == "fingers_spread":
            pose = "p"
        elif pose == "fist":
            pose = "r"
        elif pose == "wave_in":
            pose = "s"
        else:
            return

        
        #print("here")
        #print(self.player_poses)
        pose_human = pose
        #print (pose_human)
        self.player_history[0].append(pose)
        myo.vibrate('short')

        #elif myo.value == self.id_p2:
         #   pose_ai = pose
          #  self.player_history[1].append(pose)
           # myo.vibrate('short')

        #print(self.player_poses)

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

    def vibrate_lose(myo):
        myo.vibrate('long')
        myo.vibrate('long')
    
    def vibrate_win(myo):
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
    
    def vibrate_notify_connection(myo):
        myo.vibrate('short')
        time.sleep(1)
        myo.vibrate('long')
        time.sleep(1)
        myo.vibrate('short')
    
    def vibrate_tie(myo):
        myo.vibrate('short')
        

class RPSGame(Listener):
    def __init__(self):
        super(RPSGame, self).__init__()
        self.listener_changed = False
        
        self.ai = AIPlayer()
        
        # countdown, posing, post game, post match, main menu
        self.state = 'countdown'
        self.set_json_var('game_state', 'countdown')
        
        self.player_scores = [0, 0]
        #self.player_poses = ['','']
        #self.player_history = [[],[]]
        
        self.countdown_timer = 0
        self.countdown_timer_max = 3 # seconds
        self.time_intergame = 2
        
        self.start_new_match()
        #print(self.player_poses)
        
    def update(self, elapsed_secs):
        #print(self.player_poses)
        if self.state == 'countdown':      # Countdown
            self.update_countdown(elapsed_secs)
        elif self.state == 'posing':    # Posing
            if self.both_players_posed():
                self.decide_outcome()    
        elif self.state == 'post game':    # Post Game
            self.update_postgame(elapsed_secs)
        elif self.state == 'post match':    # Post Match
            self.update_post_match()
        elif self.state == 'main menu':    # Main Menu
            pass
        else:
            return

    def start_new_match(self):
        global pose_human, pose_ai
        self.ai = AIPlayer()
        self.player_scores = [0, 0]
        pose_human = ''
        pose_ai = '' 
        self.start_next_game() 

    def start_next_game(self):
        self.state = 'countdown'
        self.set_json_var('game_state', 'countdown')
        self.countdown_timer = self.countdown_timer_max
    
    def update_countdown(self, elapsed_secs):
        global pose_ai
        self.countdown_timer -= elapsed_secs
        if self.countdown_timer <= 0:
            print('OK pose now...')
            self.state = 'posing'
            self.set_json_var('game_state', 'posing')
            pose_ai = self.ai.get_pose_choice()

    
    def both_players_posed(self):
        #print("values human")
        #print(pose_human)
        #print("values ai")
        #print(pose_ai)
        return pose_human != '' and pose_ai != ''
    
    def decide_outcome(self):
        self.state = 'post game'
        self.set_json_var('game_state', 'post game')
        winner = 0
        if (pose_human == pose_ai): 
            winner = 0
            self.vibrate_tie(self.myo)
        elif (pose_human == 'r' and pose_ai == 's') or \
             (pose_human == 's' and pose_ai == 'p') or \
             (pose_human == 'p' and pose_ai == 'r'):
             # game human
             winner = 1
             self.vibrate_win(self.myo)
        else:
            # game ai
            winner = 2
            self.vibrate_lose(self.myo)        
            
        outcome = 'w' if winner == 2 else ('l' if winner == 1 else 'd')
        self.ai.update_with_game_outcome(pose_ai, pose_human, outcome)
                  
        if winner != 0: self.give_game(winner)
            
    def give_game(self, player_num):
        
        if player_num == 2: self.lose(1)
        
        print('give game to player' + str(player_num))
        
        # scores
        self.player_scores[player_num-1] += 1
        if self.player_scores[player_num-1] == 3:
            self.give_match(player_num)
            return
        # start post_game
        self.state = 'post game'
        self.set_json_var('game_state', 'post game')
        self.countdown_timer = self.time_intergame
        
    def give_match(self, player_num):
        self.state = 'post match'
        self.set_json_var('game_state', 'post match')
            
    def update_postgame(self, elapsed_secs):
        self.countdown_timer -= elapsed_secs
        if self.countdown_timer <= 0:
            self.start_next_game()
            
    def update_post_match(self):
        # query Json for state change
        if (self.get_json_var('game_state') == 'main menu'):
            self.state = 'main menu'
            self.set_json_var('game_state', 'main menu')
    
    def update_main_menu(self):
        # query Json for state change
        if (self.get_json_var('game_state') == 'countdown'):
            self.start_new_match()
            
    def set_json_var(self, id, value):      
        pass
        #with open('data.json', 'r+') as f:
            #data = json.load(f)
            #data[id] = value # <--- add `id` value.
            #f.seek(0)        # <--- should reset file position to the beginning.
            #json.dump(data, f, indent=4)
    
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
    hub.run(1000, Listener())

    start_time = time.time()
    
    # Listen to keyboard interrupts and stop the hub in that case.
    try:
        while hub.running:
            elapsed_secs = time.time() - start_time
            start_time = time.time()
            if (rps_game.listener_changed):
                print(rps_game.p1_pose, rps_game.p2_pose)
                rps_game.listener_changed=False
            rps_game.update(elapsed_secs)
            

    except KeyboardInterrupt:
        print("\nQuitting ...")
    finally:
        print("Shutting down hub...")
        hub.shutdown()

        
if __name__ == '__main__':
    main()

