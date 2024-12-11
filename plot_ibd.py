import gzip
import sys
import pandas as pd

source_pop_list = []
dest_pop_list = []
hap_count_dict = {}
snp_map_dict = {}
#dot_plot = figure(width=1500, height=800)
#ensembl_link = "http://www.ensembl.org/Bos_taurus/Location/View?r="

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

# read ibd file output by hap-ibd
with gzip.open(sys.argv[1], mode="rt") as ibd_input:
#with open(sys.argv[1]) as ibd_input:
    for line in ibd_input:
        line = line.rstrip().split()
        if (line[0] in source_pop_list and line[2] in dest_pop_list) or (
            line[2] in source_pop_list and line[0] in dest_pop_list
        ):
            sample_hap = (
                line[0] + "_" + line[1]
                if line[0] in dest_pop_list
                else line[2] + "_" + line[3]
            )
            if sample_hap not in hap_count_dict:
                hap_count_dict[sample_hap] = [[int(line[5]), int(line[6])]]
            else:
                update_window = hap_count_dict[sample_hap][:]
                overlap = False
                for i, window in enumerate(hap_count_dict[sample_hap]):
                    if (int(line[5]) >= window[0] and int(line[5]) <= window[1]) or (
                        window[0] >= int(line[5]) and window[0] <= int(line[6])
                    ):
                        update_window[i] = [
                            min(int(line[5]), window[0]),
                            max(int(line[6]), window[1]),
                        ]
                        overlap = True
                        break
                if not overlap:
                    update_window.append([int(line[5]), int(line[6])])
                hap_count_dict[sample_hap] = update_window

# read snp map file
min_cord = 999999999
max_cord = 0
with open(sys.argv[4]) as snp_map:
    for line in snp_map:
        sample_list = []
        line = line.rstrip().split()
        if sys.argv[6] == "sum_hap":
            snp_map_dict[int(line[3])] = 0
            for sample in hap_count_dict:
                window_list = hap_count_dict[sample]
                for window in window_list:
                    if int(line[3]) >= window[0] and int(line[3]) <= window[1]:
                        snp_map_dict[int(line[3])] += 1
                        if sample in sample_list:
                            print(f"windows not overlapped properly for the sample,{sample}")
                            sys.exit(1)
                        else:
                            sample_list.append(sample)
        else:
            if (int(line[3])) < min_cord:
                min_cord = int(line[3])
            if (int(line[3])) > max_cord:
                max_cord = int(line[3])

if sys.argv[6] == "sum_hap":
# write output file
    df_list = []
    with open(f"{sys.argv[5]}_num_hap.txt", "w") as dest:
        for pos in snp_map_dict:
            dest.write(f"{pos}\t{snp_map_dict[pos]}\n")
            df_list.append([pos, snp_map_dict[pos]])

# make pandas dataframe
    pd1 = pd.DataFrame(df_list, columns=["cord", "num_haplo"])

else:
    with open(f"{sys.argv[5]}_sum_anc.txt","w") as dest:
        dest.write(f"{sys.argv[5]} {max_cord-min_cord}\n")
        for sample in hap_count_dict:
            dest.write(f"{sample} {sum(i[1]-i[0] for i in hap_count_dict[sample])}\n")
