import numpy as np 
import os
import xlrd
import xlwt 
import openpyxl 
import pandas as pd 
import datetime as datetime 
import itertools
import os.path
import xlrd
import xlwt 
import openpyxl 
from pandas import ExcelWriter



class WeatherData(object): 
	"""
	WeatherData object holds file paths for source data, cleaned and reformatted data and final train and
	validation data in excel files. Methods included are for cleaning data, reindexing weather states, and
	creating train and validation data to train model on. Model information not included in this file. Users 
	need to replace data_file, clean_data_file_path, and split_data_path attributes with preferred file paths. 
	* Need to fill in filepath for df14, df15, and df16 in wrangle_data method as well. It should be same as data_file *
	"""


	def __init__(self):
		self.data_file = 'C:\\filepath\\New York Weather 2014-2016.xlsx'
		self.clean_data_file_path = 'C:\\filepath\\NY_9_States.xlsx'
		self.split_data_path = 'C:\\filepath\\NY_Train_Test_Data.xlsx'
		self.data_frames = []
		self.number_dfs = len(self.data_frames) 
		self.train_data = pd.DataFrame()
		self.test_data = pd.DataFrame()

		


	def start(self):
		"""
		Checks to see if source and destination files exist. 
		"""
		source_file_found = False

		try:
			source_file_found = os.path.isfile(self.data_file)
			if source_file_found == False: 
				raise FileNotFoundError
		except FileExistsError:
			print("The file does not exist on the path:","\n",self.data_file)
		else:
			if source_file_found == True:
				print("Source file for weather data was found.")
			pass



	
	def remove_duplicates(self,df):

		"""
		This is the function for cleaning the data. For each dataframe the index is reset and the function lambda x is applied to the 'date'
		column which sets all the 'same hour' or extra timestamp's minute field to be 51 minutes so all same hour instances are treated
		equal. Next, all same hour duplicates are dropped except for the last entry with the vast majority being at minute 51, so all 
		other hour instances are dropped for that individual hour for any date. In short, if there are exact duplicate timestamps in our 
		data or multiple records of a specific hour's weather state that differs in the minute field of the time it was taken then we 
		set these duplicates or extra records to have a timestamp minute field of 51 minutes. Then we drop all the duplicate records except for the 
		last, thus keeping only one record for each hour with a 51 minute field in the timestamp. 
		"""
		df = df.reset_index()   # Reset the data frame's index 
		df['date'] = df['date'].apply(lambda x: x.replace(minute=51, second=0)) # Set all minute fields to 51 minutes
		df = df.drop_duplicates(subset='date', keep = 'last') # Drop all duplicate or extra records except for the last
		

		return df



	def insert_row(idx, df, df_insert):
		# Insert row into data frame where missing hour/row is. Resets index and returns new data frame
	    return df.iloc[:idx, ].append(df_insert).append(df.iloc[idx:, ]).reset_index(drop = True)

	def fill_missing_data(self,df): 
		"""
		Fill in missing data with the data from the previous hour. This means setting a missing rows data
		equal to the previous rows data. We check if a row is missing if there is an hour that is different
		from our date_rng object's hour at the same index. If missing, we call the insert_row method to 
		insert the missing row with the last rows data. 
		"""

		for i in range(len(date_rng)): 

			if(i != 0): 
				last_hour = df['date'][i-1]

			if df['date'][i] != date_rng[i]: 
				df = insert_row(i,df,last_hour)


		return df



	def reindex_weather_states(self,df):
		"""
		This method reindexes the 'Condition' column holding the weather state represented by an integer value ranging 
		from 0-5 to a more distinct weathers state based on a table indexing the weather states made from columns
		'Weather States' and 'Index' which are located in columns Y and Z respectively in the excel files. This gives
		each distinct string in column 'Weather' (R in excel) its own integer representing that weather state. Since 
		many weather states are very similar we can group the newly indexed weather states into 9 different weather 
		categories with similar weather states grouped together. These new categories indexed 1-9 will be reindexed 
		again to 0-8 so that we can use the results for training and predicting with a neural network later.  
		"""

		# Create the final range of integer values to index the weather states/categories to be used later
		new_states = []
		for i in range(1,29): 
			new_states.append(i)
		
		# Nested for loop to reindex the integer values of the weather states so that the same number of 
		# weather state strings and weather state integer values are equal. The new range of integer values
		# for the weather states are 0-28 for a total of 29. 
		for i, j in itertools.product(range(len(df)), range(29)): # i loops through data frame. j loops through new weather state index table in column 24 of data frame
		
			# If the weather condition strings match, assign new weather state integer value to same row in column 22
			# that holds the newly indexed weather states. 
			if df.iat[i,16] == df.iat[j,23]: #if the weather states are the same, correct and assign the proper index/condition integer
				df.iat[i,22] = df.iat[j,24]

		# The following code removes the 'Unknown' weather state 0 and replaces it with the last rows/hours
		# weather states integer value
		for i in range(len(df)): 
			
			if df.iat[i,22] == 0:
			
				if df.iat[i-1,22] != 0:
					df.iat[i,22] = df.iat[i-1,22] # Convert unknown weather states into previous hours weather state
					
				elif df.iat[i-1,22] == 0:
					try: 
						# If previous hours weather state is zero, set current weather state to the next rows weather state
						# raise error if there are three unknown weather states in a row
						df.iat[i,22] = df.iat[i+1,22] 
						if df.iat[i+1,22] == 0 and df.iat[i-1,22] == 0: 
							raise ValueError
					except ValueError: 
						print("Error: There are three unkown weather states in a row.")
		# Final test if zero integer value was removed from the weather states. 
		# Checks for successful conversion of all 'uknown' weather states in the 'True Condition' column
		weather_states = []
		try: 
			weather_states = df['True Condition']
			if 0 in weather_states: 
				raise ValueError

		except ValueError: 
			print("The data frames weather states still contain zero(s).")

		# Convert 29 weather states into 9 weather categories (1-9) by grouping similar weather states
		# such as thunderstorms and heavy thunder storms together. The first four weather states are the
		# most distinct from each other and can therefore represent single categories. 
		
		for i in range(len(df)): 

			k = df.iat[i,22]

			if k == 6: 
				df.iat[i,22] = 5
			elif k in new_states[7:11]: 
				df.iat[i,22] = 6
			elif k in new_states[11:16]: 
				df.iat[i,22] = 7
			elif k in new_states[16:21]: 
				df.iat[i,22] = 8
			elif k > 20: 
				df.iat[i,22] = 9
		# Here we reduce the states integer values by one to include zero again for 
		# processing data in our nerual networks later
		for i in range(len(df)): 
			df.iat[i,22] = df.iat[i,22] -1 
			 

		return df

	def get_date_range(self,year):
		# Create date ranges for years of interest to compare with data frames timestamps in order
		# to find missing rows once duplicates have been removed.

		if(year == 2014):
			date_rng = pd.date_range(start='1/1/2014 00:51:00', end='12/31/2014 23:51:00', freq='H')
		if(year == 2015):
			date_rng = pd.date_range(start='1/1/2015 00:51:00', end='12/31/2015 23:51:00', freq='H')
		if(year == 2016):
			date_rng = pd.date_range(start='1/1/2016 00:51:00', end='12/31/2016 23:51:00', freq='H')
		
		return date_range


	def check_df_length(self,df,year):
		"""
		Check to make sure data frames are correct length based on how many hours are in that year. 
		For a regular year there are 8760 hours and for a leap year (2016 in this case) there
		are 8784 hours since there is an extra day. 
		"""
		df_length = True

		if(year == 2014 or year == 2015):
			if(len(df) != 8760):
				df_length = False 
				
		if(year == 2016):
			if(len(df) != 8784):
				df_length = False 
		
		return df_length


	def clean_data(self,df,year):

		correct_length = True

		date_range = self.get_date_range(year)
		# remove duplicates from data frame based on duplicate timestamps
		df = self.remove_duplicates(df)
		# Fill in missing rows of data frame
		df = self.fill_missing_data(df)
		
		try:
	  		correct_length = check_df_length(df,year)
	  		if correct_length == False:
	  			raise LengthError

		except LengthError:
	  		print("Length of ", year, " data frame is incorrect.")
	  		print("The resulting length is:", len(df))
		
		return df

	def get_features(self,df): 
		"""
		This method accepts the data frame and creates a new data frame with only the columns of interest.
		These columns will be the features to train the model on. 
		"""
		features = ['date','Temp (F)','dew_pt','hum','Wind Speed (m/s)','vis','pressure','True Condition']
		new_df = df[['date','Temp (F)','dew_pt','hum','Wind Speed (m/s)','vis','pressure','True Condition']].copy()
		return new_df


	def create_train_and_test_data(self):

		data = self.data_frames
		# concatenate 2014 and 2015 data frames as both will be used for the training data
		self.train_data = pd.concat(data[0:2])
		# reset the index after concatenation
		self.train_data = self.train_data.reset_index(drop=True)
		# assign validation data to the third data frame containing 2016 weather data
		self.test_data = data[2]


	# This function is for sending the resultant transition matrix data frames to excel
	def save_xls(self,list_dfs,dataset_name,path):

		#xls_path = The path to your excel file
	
		with ExcelWriter(path) as writer: 
			for n, df in enumerate(list_dfs):
				df.to_excel(writer,dataset_name[n])
			writer.save()

	def wrangle_data(self):
		"""
		Method calls all necessary methods. 
		* Need to fill in filepath for df14, df15, and df16 *
		"""

		df14 = pd.ExcelFile('C:\\filepath\\New York Weather 2014-2016.xlsx').parse('2014',index_col=0)
		df15 = pd.ExcelFile('C:\\filepath\\New York Weather 2014-2016.xlsx').parse('2015',index_col=0)
		df16 = pd.ExcelFile('C:\\filepath\\New York Weather 2014-2016.xlsx').parse('2016',index_col=0)
		
		source_path = self.data_file
		dest_path = self.clean_data_file_path
		frames = [df14, df15, df16]
		df_list = []
		years = ['2014','2015','2016']
		year = [2014, 2015, 2016]
		test_and_train_data = [] 
		split_data = ['train_data(2014-2015)','test_data(2016)']
		split_data_path = self.split_data_path

		# Loop through data frames and call necessary methods to obtain final data frames to build 
		# train and validation data from. 
		for i in range(0,3):
			df = self.clean_data(frames[i],year[i])
			df = self.reindex_weather_states(df)
			df = self.get_features(df)
			df_list.append(df)
		self.data_frames = df_list

		self.save_xls(df_list,years,dest_path)	
		print("All data frames have been cleaned and saved to excel file on path: ",'\n' , dest_path)


		self.create_train_and_test_data()
		
		test_and_train_data.append(self.train_data)
		test_and_train_data.append(self.test_data)
		self.save_xls(test_and_train_data,split_data,split_data_path)
		print("Training and testing data have been made and saved to excel file on path: ",'\n' , split_data_path)


		
		


