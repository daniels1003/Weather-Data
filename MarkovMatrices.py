import numpy as np 
import os
import xlrd
import xlwt 
import openpyxl 
import pandas as pd 
import datetime as datetime 
import itertools


"""
 This function is to be called on for creating a markov or transition matrix from a data frame
 given a data frame as the argument 'df' and the number of transition states in the matrix as 
 the argument 'num_states'. in terms of granularity of the time period for creating the yearly 
 transition matrix for the New York weather with varying granularity: monthly, seasonal or yearly matrices.
 # Function returns the states counts as well as the markov matrix. 
"""
def create_markov_matrix(df,num_states):

	# For a markov matrix the number of transition states in the matrix must be an integer. 
	if not type(num_states) is int: 
		raise TypeError("Only intergers are allowed for the number of states in the matrix")
	 

	# Initialize state_counts as an array of zeros that holds the number of weather states
	state_counts = np.zeros(num_states) 
	# Initialize Transitional_matrix as a 2-Dimensional array of zeros. 
	Transitional_matrix = np.zeros((num_states,num_states))

	i = 0

	while i < len(df) - 1: 
		# We consider every state except the last listed in the data frame because the last
		# state will not have a following state and thus we cannot assign a value for it in 
		# the initial step of constructing the transition matrix. 

			condition = df.iat[i,22]    # This sets the variable condition to equal the weather condition or state in the data 
										# frame which is in the 22nd column of the data frame. 
			following_condition = df.iat[i+1,22]

			if type(condition) != type(following_condition): 
				raise TypeError("To build the matrix, condition and following_condition must be the same type.")
			"""
			Creates a nested for loop to have variables 'condition' and 'following_condition' loop 
			through all 29 (whatever 'num_states' is set to) integer valued weather states until the 
			current weather condition and following weather condition are found. 
			"""
			for j, k in itertools.product(range(num_states),range(num_states)):    
								   # values. It will start with 0 and end at 28. 
				if condition == j:              # If the variable 'condition' equals j, add one to the position in the state count 
					state_counts[j] += 1
				"""     
				 This code segment sets the variable 'following_condition' to the next 
			     hours weather condition from the dataframe. This is done by choosing 
				 the 'i+1'th hour's weather state and similar to the first state we 
                 chose for 'condition', we determine its indexed-integer value by looping
                 through the possible states(equal to 'num_states'). When a match is found we add 1 to the 
			     corresponding position in the 2-D transition matrix by using 'i' or 'condition'
			     to indicate the row and 'k' or 'following_condition' to indicate the column. 
				"""
				if following_condition == k:		
					Transitional_matrix[condition][following_condition] += 1 
					
		i += 1

	for i, j in itertools.product(range(num_states),range(num_states)):
	# for i in range(num_states): # Loop through each row i in the transition matrix 
	#	for j in range(num_states): # Loop through every column in each row in the matrix 
		if state_counts[i] == 0 or Transitional_matrix[i][j] == 0: # This line ensures we dont have a zero in the numerator or 
			Transitional_matrix[i][j] = 0							 # denominator for calculating every position in the transition
		else:															 # matrix. 
			Transitional_matrix[i][j] = np.around(Transitional_matrix[i][j] / state_counts[i],decimals = 8) 
	# The 'np.around()' function rounds the result of the division operation to a specified number of decimals
	# Here we chose 8 decimals. Since we are limiting the number of decimals allowed to each position in the matrix
	# the total probability in each row might be slightly less than one but it is still understood that the total
	# probability of each row in the matrix should amount to 1.  
	
	
	return state_counts, Transitional_matrix