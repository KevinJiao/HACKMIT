import sys
import random



class Game(object):
	def __init__(self):
		# poses are  'r', 'p', or 's' ('' means non existing game)
		self.pose_ai = ''  
		self.pose_human = ''
		
		# outcome is 'w', 'l', 'd' ('' means non existing game)
		self.outcome = '' 
	
	def __str__(self):
		return self.pose_ai + self.pose_human + self.outcome
	

def random_pose():
	return "rps"[int(random.random() * 3)]

def valid_state(state):
	return len(state) == 3 # <ai pose> <human pose> <outcome> <action>

def find_greedy_pose(q_matrix, current_state):
	if (not valid_state(current_state)) or len(q_matrix) == 0:
		return 0, random_pose()
	else:
		# find the best pose with the current state
		max_q = -sys.maxint - 1
		best_pose = random_pose()
		
		for i in range(len(q_matrix)):
			state = q_matrix.keys()[i][0:3]
			
			if state != current_state: continue # only look at q matrix entries with current state
			
			if q_matrix.values()[i] > max_q:
				max_q = q_matrix.values()[i]
				
				action = q_matrix.keys()[i][-1]
				best_pose = action
				
		return max_q, best_pose
	

GREEDY_CHANCE = 1

def main():
	
	prev_games = []
	q_matrix = dict()
	
	wins_ai = 0
	wins_human = 0
	num_games = 50
	debug = True
	human_pattern = ['r', 'p', 'r', 's' 'r', 'p', 's', 's', 's']
	
	for i in range(num_games):
		
		pose_ai = ''
		pose_human = ''
		state = '' if (len(prev_games) == 0) else str(prev_games[-1])
		
		#-----------------------------------------
		# Determine poses
		
		q_greedy, pose_greedy = find_greedy_pose(q_matrix, state)
		
		if debug: print 'Q Matrix: ', q_matrix
		
		if random.random() <= GREEDY_CHANCE and q_greedy > 0:
			# pick greedily
			pose_ai = pose_greedy
			if debug: print 'picks greedy - q = ' + str(q_greedy)
		else:
			# pick randomly
			pose_ai = random_pose()
			if debug: print 'picks random'
		
		
		# human picks random pose
		#pose_human = str(raw_input('enter r, p, or s: '))
		#pose_human = random_pose()
		pose_human = human_pattern[i % 3]
		
		#-----------------------------------------
		# Game outcome
		
		game = Game()
		game.pose_ai = pose_ai
		game.pose_human = pose_human
		game.outcome = 'd' if pose_ai == pose_human else \
					   'w' if ((pose_ai == 'r' and pose_human == 's') \
						   or (pose_ai == 'p' and pose_human == 'r' ) \
						   or (pose_ai == 's' and pose_human == 'p' )) \
						   else 'l' 
						   
		print 'game: ', game
		print
		
		if game.outcome == 'w': wins_ai += 1
		elif game.outcome == 'l': wins_human += 1
						   
		# save game to history
		prev_games.append(game)
		
		#-----------------------------------------
		# Update q matrix
		
		if (valid_state(state)):			
			state_action_pair = state + pose_ai
			
			# create q_matrix entry if not yet existent
			if not state_action_pair in q_matrix.keys():
				q_matrix[state_action_pair] = 0
				
			# reward for ai pose choice given previous game
			q_matrix[state_action_pair] += 1 if game.outcome == 'w' else (-1 if game.outcome == 'l' else 0)
			
			
		
	print 'AI won ' + str((float(wins_ai) / (wins_ai + wins_human)) * 100.0) + '% of won games'	
		
		
		
#-----------------------------------------
# Entry Point
main()
		
		