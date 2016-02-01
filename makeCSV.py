
import csv
import os

def get_mods(file):
	mods = {}
	with open(file, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			if len(row) > 1:
				if row[0] not in mods:
					mods[format_frase(row[0])] = list()
				mods[format_frase(row[0])].append(row[3])
	return mods

def format_frase(string):
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
					translation[format_frase(row[0])] = format_frase(row[1])
	
	return translation

def make_translation_list(mods, translation):
	translation_list = []
	for frase, trans in translation.items():
		if frase in mods:
			for mod in mods[frase]:
				translation_list.append([frase, trans, 'module', mod])

	return sorted(translation_list, key=lambda x: x[3])

def make_untranslated_list(mods, translation):
	untranslated_list = []
	for mod in mods:
		if mod not in translation:
			untranslated_list.append(mod)

	print untranslated_list

def write_new_csv(translation_list, out_filename):
	with open(out_filename, 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', doublequote='true', quoting=csv.QUOTE_NONNUMERIC)
		for list_item in translation_list:
			writer.writerow(list_item)

def main():
	mods = get_mods('magento2_frases.csv')
	translation = get_translations('vaimo_italian/app/locale/it_IT/')
	translation_list = make_translation_list(mods, translation)
	write_new_csv(translation_list, 'it_IT.csv')
	make_untranslated_list()

main()