import gzip
import sys
import pandas as pd

source_pop_list = []
dest_pop_list = []
hap_count_dict = {}
snp_map_dict = {}

#the column names of new dataframe
pd_dict = {
    "source_sample": [],
    "ss_hap": [],
    "target_sample": [],
    "ts_hap": [],
    "chrom": [],
    "start": [],
    "end": [],
    #"size_in_cm": [],
}
key_list = list(pd_dict.keys())

# read file containing source population/sample ids
with open(sys.argv[2]) as source_pop:
    for line in source_pop:
        pop = line.rstrip().split()[1]
        source_pop_list.append(pop)

# read file containing target population/sample ids
with open(sys.argv[3]) as dest_pop:
    for line in dest_pop:
        pop = line.rstrip().split()[1]
        dest_pop_list.append(pop)

# read coordinate-sorted output of hapIBD --> this coordinate-sorted file will be used to calculate number of shared IBD in FL with RH. 
with gzip.open(sys.argv[1], mode="rt") as ibd_input:
    for line in ibd_input:
        line = line.rstrip().split()
        n_line = []
        if (line[0] in source_pop_list and line[2] in dest_pop_list) or (
            line[2] in source_pop_list and line[0] in dest_pop_list
        ):
            ##this code will make sure that we always have source sample in the first column and taget sample in the third column
            if line[2] in source_pop_list:
                n_line = [
                    line[2],
                    line[3],
                    line[0],
                    line[1],
                    line[4],
                    line[5],
                    line[6],
                    #line[7],
                ]
            elif line[0] in source_pop_list:
                n_line = line[:]
            else:
                pass
            if len(n_line) == 0:
                print("record cannot be zero, problem with file")
                sys.exit(0)
            else:
                for i, v in enumerate(n_line):
                    pd_dict[key_list[i]].append(v)

new_df = pd.DataFrame.from_dict(pd_dict)
new_df = new_df.astype({"start":int,"end":int})
new_df = new_df.sort_values(['target_sample','ts_hap',"start","end"])
new_df.to_csv(sys.argv[4]+"_target_sample_sorted.txt",index=False)
