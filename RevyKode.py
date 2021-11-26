import numpy as np
import pandas as pd
from collections import Counter
import itertools

class Schedule():
	
	def __init__(self, roles_csv, times_csv, no_materials, no_participants):
	
		self.roles_csv=roles_csv
		self.times_csv=times_csv
		self.no_materials=no_materials
		self.no_participants=no_participants
		
		self.all = pd.read_csv(self.roles_csv)
		self.times = pd.read_csv(self.times_csv)

		self.all.index = self.all['Unnamed: 0'].rename('Name')
		self.all = self.all.T.drop('Unnamed: 0')
		self.all = self.all[: self.no_materials ].T[: self.no_participants ]

		self.day = self.times.columns.to_numpy()[0]
		self.available_times = self.times[self.day].dropna().index
		self.times = self.times.T[self.available_times][:].T
		self.times.index = self.times[self.day]

		self.participants = self.times.T.index[1:]
		self.sceneParticipants = self.all.index[1:]
	
	
	def all_sketches(self):
		'''
		Returns a list (numpy array) with all sketches.
		'''
		return self.all.columns.to_numpy()
	
	def all_participants(self, scene=False):
		'''
		Returns a list (numpy array) with all participants in the revu.
		
			scenen : if set to True, returns only participants present in songs or sketches.
		'''
		if scene:
			return self.sceneParticipants.to_numpy()
		else:
			return self.participants.to_numpy()
	
	
	def get_participants(self, sketch_name):
		'''
		Returns all participants of a given song/sketch.

			sketch_name : name of the given sketch.
		'''
		return self.all[ sketch_name ].dropna().index.to_numpy()
	
	
	def get_sketches(self, participant_name):
		'''
		Returns all sketches of a given participant.

			participant_name : name of the given participant.
		'''
		return self.all.T[ participant_name ].dropna().index.to_numpy()
	
	
	def get_unattended(self, participant_name):
		'''
		Returns the time frames in which a participant is unavailable.
		If no times are available the participant will be labelled "Booked all day".

			participant_name : name of the given participant.
		'''
		notpresent = self.times[ participant_name ].dropna().index.to_numpy()
		if len(notpresent) == len(self.available_times):
			notpresent = ['Booked all day']
		else:
			pass
		return notpresent
	

	def crossref(self, sketch_list):
		'''
		Cross references a list of sketches to examine whether there are any overlap of participants.
		Returns a dataframe with the participants, the number of sketches/songs in which they participate
		and the number of overlaps.

			sketch_list : list of sketches to be cross referenced.
		'''
		list_of_people = []
		for sketch in sketch_list:
			list_of_people.extend(self.get_participants(sketch))
		list_of_people = Counter(list_of_people)
		pandafied_list = pd.DataFrame.from_dict(dict(list_of_people),orient='index')
		
		pandafied_list.rename( columns={0 :'Booknings'}, inplace=True )
		
		# Adds availability:
		pandafied_list['Availability'] = self.get_available_for_crossref()
		
		# Adds sketches that clash:
		sketch_issues = []
		for participant in list(list_of_people):
			sketch_issues.append(str(set(self.get_sketches(participant)).intersection(sketch_list))[1:-1])
		pandafied_list['SketchClash'] = sketch_issues
		
		return pandafied_list.sort_values('Booknings', ascending=False)

	def get_available(self):
		'''
		Returns a pandas dataframe with all participants divided into whether they are available
		all day, some of the day or booked all day.
		'''
		available_all_day = []
		partly_available = []
		unavailable = []
		for participant in self.participants:
			notpresent = self.get_unattended(participant)
			if len(notpresent) == len([]):
				available_all_day.append(participant)
			elif notpresent[0] == 'Booked all day':
				unavailable.append(participant)
			else:
				partly_available.append(participant)
		pdavailable = pd.DataFrame([available_all_day, partly_available, unavailable], index = ['available_all_day', 'partly_available', 'unavailable']).T
		return pdavailable
		
	def get_available_for_crossref(self):
		'''
		Helping function for the function crossref.
		'''
		
		participants_list = []
		available = []
		
		for participant in self.participants:
			notpresent = self.get_unattended(participant)
			if len(notpresent) == len([]):
				participants_list.append(participant)
				available.append('available_all_day')
			elif notpresent[0] == 'Booked all day':
				participants_list.append(participant)
				available.append('partly_available!')
			else:
				participants_list.append(participant)
				available.append('booked!')
				
		pdavailable = pd.DataFrame([participants_list, available]).T
		
		pdavailable.index = participants_list
		pdavailable = pdavailable.T.drop(0).rename({1 :'Availability'}).T
		
		return pdavailable
	
	def optimal_distribution(self, a_series_of_skeches, available_rooms):
		'''
		This functions returns the optimal distribution of the different sketches after applying
		the crossref-function.

			a_series_of_skeches : the sketches to be analysed.
			available_rooms : number of available rooms.
		'''
		
		list_of_lists = []
		for a_combination in itertools.combinations(a_series_of_skeches, available_rooms):
		
			crossreffed_list = self.crossref(list(a_combination))
			
			no_participants = len(crossreffed_list['Booknings'].to_numpy())
			total_no_booknings = crossreffed_list['Booknings'].sum()
			
			if no_participants == total_no_booknings:
				list_of_lists.append(list(a_combination))
		
		if len(list_of_lists) == 0:
			list_of_lists.append('No good combinations')
		
		return list_of_lists
			

sche = Schedule(roles_csv='Roles.csv',
				times_csv='Times.csv',
				no_materials=25,
				no_participants=41)


some_sketches = ['Introsang','Karrieredag','Mappedyr', 'ff Enheder', 'Ninjasangen', 'Krænkevise']

opt_dist = sche.optimal_distribution(some_sketches, available_rooms=4)

print(opt_dist)

