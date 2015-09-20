import sys
import random



class GameInfo(object):
	def __init__(self):
		# poses are  'r', 'p', or 's' ('' means non existing game)
		self.pose_ai = ''  
		self.pose_human = ''
		
		# outcome is 'w', 'l', 'd' ('' means non existing game)
		self.outcome = '' 
	
	def __str__(self):
		return self.pose_ai + self.pose_human + self.outcome
	
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
		
		if self.debug: print 'Q Matrix: ', self.q_matrix
		
		if random.random() <= self.greedy_chance and q_greedy > 0:
			# pick greedily
			pose = pose_greedy
			if self.debug: print 'picks greedy - q = ' + str(q_greedy)
		else:
			# pick randomly
			pose = self.random_pose()
			if self.debug: print 'picks random'
			
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
		
		

def main():
	
	ai = AIPlayer()
	
	wins_ai = 0
	wins_human = 0
	num_games = 50
	human_pattern = ['r', 's', 's', 'r', 'p', 'p', 's']
	
	for i in range(num_games):
		
		pose_ai = ''
		pose_human = ''
		
		#-----------------------------------------
		# Determine poses
		
		
		pose_human = human_pattern[i % 7]
		pose_ai = ai.get_pose_choice()
		
		#-----------------------------------------
		# Game outcome
		
		outcome = 'd' if pose_ai == pose_human else \
					   'w' if ((pose_ai == 'r' and pose_human == 's') \
						   or (pose_ai == 'p' and pose_human == 'r' ) \
						   or (pose_ai == 's' and pose_human == 'p' )) \
						   else 'l'
						   
		ai.update_with_game_outcome(pose_ai, pose_human, outcome)
						   
		print 'human: ' + pose_human + ' ai: ' + pose_ai + ' outcome: ' + 'ai win? ' + outcome
		print
		
		if outcome == 'w': wins_ai += 1
		elif outcome == 'l': wins_human += 1
						  
		
	print 'AI won ' + str((float(wins_ai) / (wins_ai + wins_human)) * 100.0) + '% of won games'	
		
		
		
#-----------------------------------------
# Entry Point
main()
		
		