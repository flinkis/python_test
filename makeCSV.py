#!/usr/bin/env python
import csv, os, sys, getopt

def get_mods(file):
	mods = {}
	with open(file, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			if len(row) > 1:
				if row[0] not in mods:
					mods[format_phrase(row[0])] = list()
				mods[format_phrase(row[0])].append(row[3])
	return mods

def format_phrase(string):
	i = 1
	while string.find('%s') >= 0:
		string = string.replace('%s', '%'+str(i), 1)
		i = i + 1	
	return string

def walk_directory(directory):
	list_of_files = []
	for subdir, dirs, files in os.walk(directory):
		for file in files:
			if os.path.splitext(file)[1] == '.csv':
				list_of_files.append(directory+file)
	return list_of_files

def get_translations(directory):
	translation = {}
	for file in walk_directory(directory):
		with open(file, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', skipinitialspace='true')
			for row in reader:	
				if len(row) > 1:
					translation[format_phrase(row[0])] = format_phrase(row[1])
	
	return translation

def make_translation_list(mods, translation):
	translation_list = []
	for phrase, trans in translation.items():
		if phrase in mods:
			for mod in mods[phrase]:
				translation_list.append([phrase, trans, 'module', mod])

	return sorted(translation_list, key=lambda x: x[3])

def make_untranslated_list(mods, translation):
	untranslated_list = []
	for phrase in mods:
		if phrase not in translation:
			for mod in mods[phrase]:
				untranslated_list.append([phrase, phrase, 'module', mod])

	return sorted(untranslated_list, key=lambda x: x[3])

def write_new_csv(phrases_list, out_filename):
	with open(out_filename, 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', doublequote='true', quoting=csv.QUOTE_NONNUMERIC)
		for list_item in phrases_list:
			writer.writerow(list_item)

def main():
	magento2_translation = 'magento2_phrases.csv'
	translation_file_directory = ''
	outpu_file_name = ''

	try:
		myopts, args = getopt.getopt(sys.argv[1:],"d:o:")
	except getopt.GetoptError as e:
		print (str(e))
		print("Usage: %s -d input -o output " % sys.argv[0])
		sys.exit(2)
 
	for key, value in myopts:
		if key == '-d':
			translation_file_directory = value
		elif key == '-o':
			outpu_file_name = value

	mods = get_mods(magento2_translation)
	translation = get_translations(translation_file_directory)

	translation_list = make_translation_list(mods, translation)
	untranslated_list = make_untranslated_list(mods, translation)

	write_new_csv(translation_list, outpu_file_name+'.csv')
	write_new_csv(untranslated_list, outpu_file_name+'_untranslated.csv')
	
if __name__ == "__main__":
	main()