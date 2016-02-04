#!/usr/bin/env python

import csv, os, sys, getopt, difflib

def get_mods(file):
	mods = {}
	with open(file, 'rb') as csvfile:
		reader = csv.reader(csvfile, escapechar="\\")
		for row in reader:
			if len(row) > 1:
				if row[0] not in mods:
					mods[row[0]] = list()
				mods[row[0]].append(row[3])
	return mods

def format_phrase(string):
	counter = 1
	while string.find('%s') >= 0 or string.find('%d') >= 0:
		index = min(i for i in [string.find('%s'), string.find('%d')] if i >= 0)
		string = string[0:index+1] + str(counter) + string[index+2:]
		counter = counter + 1
	
	string = string.replace('""', '"')
	return string

def walk_directory(directory):
	list_of_files = []
	for dirpath, dirnames, filenames in os.walk(directory):
		for name in filenames:
			if os.path.splitext(name)[1] == '.csv':
				list_of_files.append(os.path.join(dirpath, name))
	return list_of_files

def get_translations(directory):
	translation = {}
	for file in walk_directory(directory):
		with open(file, 'rb') as csvfile:
			reader = csv.reader(csvfile, escapechar="\\")
			for row in reader:	
				if len(row) > 1:
					translation[format_phrase(row[0])] = format_phrase(row[1])
	
	return translation

def append_translation_item(phrase1, phrase2, mods, translation_list, skip_duplicate_items):
	if skip_duplicate_items:
		translation_list.append([phrase1, phrase2])
	else:
		for mod in mods[phrase1]:
			translation_list.append([phrase1, phrase2, 'module', mod])
	return translation_list

def make_translation_list(mods, translation, skip_duplicate_items, disable_fuzzy_search, fuzzy_search_cutouff, pick_fuzzy_search):
	translation_list = []
	for phrase, trans in translation.items():
		if phrase in mods:
			translation_list = append_translation_item(phrase, trans, mods, translation_list, skip_duplicate_items)
		elif not disable_fuzzy_search:
			closest_match = difflib.get_close_matches(phrase, mods, cutoff=fuzzy_search_cutouff)
			if closest_match:
				if len(closest_match) >= 2 and pick_fuzzy_search:
					print 'Original Prase:', phrase
					for alternative in closest_match:
						print '[' + str(closest_match.index(alternative)) + ']', alternative
					print '[' + str(len(closest_match)) + ']', 'None of the above'
					print ''
					try:
						input= int(raw_input("Pick an alternative [0]: "))
					except ValueError:
						input = 0
					if input < len(closest_match):
						translation_list = append_translation_item(closest_match[input], trans, mods, translation_list, skip_duplicate_items)
				else:
					translation_list = append_translation_item(closest_match[0], trans, mods, translation_list, skip_duplicate_items)
	
	if not skip_duplicate_items:				
		translation_list = sorted(translation_list, key=lambda x: x[3]) 
	return translation_list

def make_untranslated_list(mods, translation, skip_duplicate_items):
	untranslated_list = []
	for phrase in mods:
		if not phrase in [list_item[0] for list_item in translation]:
			translation_list = append_translation_item(phrase, phrase, mods, untranslated_list, skip_duplicate_items)
	
	if not skip_duplicate_items:
		untranslated_list = sorted(untranslated_list, key=lambda x: x[3])
	return untranslated_list

def write_new_csv(phrases_list, out_filename):
	with open(out_filename, 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', doublequote='true', quoting=csv.QUOTE_NONNUMERIC)
		for list_item in phrases_list:
			writer.writerow(list_item)

def print_usage_and_quit():
	print("USAGE:\n"+
	"This script combine several csv files to a a single file\n"+
	"and changes m1 names to m2 compatible names\n"+
	"\n"+
	"OPTIONS:\n"+
	"   -h  |  --help              print this message\n"+
	"   -i  |  --input             path to target directory\n"+
	"   -o  |  --output            output filename\n"+
	"   -f  |  --disable-fuzzy     (optional) disable fuzzy search\n"+
	"   -c  |  --fuzzy-cutoff      (optional) fuzzy search cutoff [0-1] (default: 0.85)\n"+
	"   -p  |  --pick-alternative  (optional) pick fuzzy alternative\n"+
	"   -u  |  --untranslated      (optional) create csv with untranslated phrases\n"+
	"   -d  |  --skip-duplicates   (optional) skip duplicate phrases\n")
	sys.exit(2)

def main():
	magento2_translation = 'magento2_phrases.csv'
	translation_file_directory = ''
	outpu_file_name = ''
	skip_duplicate_items = False
	make_untranslated_csv = False
	disable_fuzzy_search = False
	pick_fuzzy_search = False
	fuzzy_search_cutouff = 0.85

	try:
		myopts, args = getopt.getopt(sys.argv[1:], "i:o:fvc:pduh", ['help', 'input=', 'output=', 'disable-fuzzy', 'fuzzy-cutoff=', 'pick-alternative', 'skip-duplicates', 'untranslated'])
	except getopt.GetoptError as e:
		print (str(e))
		print_usage_and_quit()
		
	for key, value in myopts:
		if key in ("-i", "--input"):
			if os.path.isdir(value):
				translation_file_directory = value
			else:
				print_usage_and_quit()
		elif key in ("-h", "--help"):
			print_usage_and_quit()
		elif key in ("-o", "--output"):
			outpu_file_name = value
		elif key in ("-f", "--disable-fuzzy"):
			disable_fuzzy_search = True
		elif key in ("-c", "--fuzzy-cutoff"):
			try:
				fuzzy_search_cutouff = float(value)
			except ValueError:
				fuzzy_search_cutouff = 1.0
		elif key in ("-p", "--pick-alternative"):
			pick_fuzzy_search = True
		elif key in ("-d", "--skip-duplicates"):
			skip_duplicate_items = True
		elif key in ("-u", "--untranslated"):
			make_untranslated_csv = True

	if translation_file_directory == '' or outpu_file_name == '':
		print_usage_and_quit()

	mods = get_mods(magento2_translation)
	translation = get_translations(translation_file_directory)

	translation_list = make_translation_list(mods, translation, skip_duplicate_items, disable_fuzzy_search, fuzzy_search_cutouff, pick_fuzzy_search)
	write_new_csv(translation_list, outpu_file_name+'.csv')

	if make_untranslated_csv:
		untranslated_list = make_untranslated_list(mods, translation_list, skip_duplicate_items)
		write_new_csv(untranslated_list, outpu_file_name+'_untranslated.csv')
	
if __name__ == "__main__":
	main()