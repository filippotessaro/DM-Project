# this script is useful to print out the time employed by the algorithm wrt the increasing number of lines
import subprocess
import datetime
import argparse

# Construct the argument parser
ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument("-o", "--output_txt_file", required=True,
   help="output txt file")
args = vars(ap.parse_args())

result_file = str(args['output_txt_file'])

dataset_size = [10000, 20000, 50000, 100000, 500000 , 1000000]

def Log2FileResults(result, result_file):
	f = open(result_file, "a+")
	f.write(str(result) + "\n")
	f.close()


def normalize_datasets(infile_name):
	baskets = []
	with open(infile_name, 'r') as f:
		for line in f:
			basket = []
			line = line[:-1]
			items = line.split(",")
			for item in items:
				basket.append(item)
			baskets.append(basket)

	elems = set()
	for b in baskets:
		elems.update(b)

	mapping = {}
	reverseMapping = {}
	key = 0
	for basket in elems:
		mapping[basket] = key
		reverseMapping[key] = basket
		key += 1

	dict = open("../Data/normalized_dictionary.txt", "w")
	dict.write(str(mapping))
	dict.close()

	file_out = "../Data/sintetic/test" + str(i) + "norm.csv"

	ds = open(file_out, 'w')
	for basket in baskets:
		line_file = ''
		for item in basket:
			line_file += str(mapping[item]) + ','
		line_file = line_file[:-1]
		ds.write(line_file + '\n')
	ds.close()

	print('End Normalization')
	return file_out


for i in dataset_size:
	print("Size: " + str(i))
	print("start norm")
	filename = "../Data/sintetic/test" + str(i) + ".csv"

	file_norm = normalize_datasets(filename)

	print(file_norm)

	start = datetime.datetime.now()

	support = int(i * 1.5/100)
	bashCommand = "python3 apriori_rulgen.py -a " + file_norm + " -b ../Data/frequent_itemsets.txt -c ../Data/normalized_dictionary.txt -d ../Data/association_rules.txt -sup " +str(support)+ " -conf 0.4"
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()
	end = datetime.datetime.now()
	time_elapsed = end - start
	print("End size: ", str(i), "\t Time time elapsed:", str(time_elapsed))
	result = "Size: ", str(i), "\t - Apriori Time time elapsed:", str(time_elapsed)
	Log2FileResults(result, result_file)


