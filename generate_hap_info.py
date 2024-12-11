import sys
import re
import pandas as pd
from infer_haps_utils import merge_overlap_tar_haps

"""
this python script inferred donor haplotypes based on the csv input file which is sorted based on the start (second col) and end coordinates (third col)

example input file:

ASR21337_1,84945,13008583,HF0078_1:84945-13008583
ASR23291_1,84945,13037346,HF0087_2:84945-13037346 HF0799_2:84945-13037346 KI-GT0942_1:84945-13037346
ASR05228_1,84945,13202529,DA0000_1:84945-13202529 HF0619_2:84945-13202529 HF0894_2:84945-13202529 KI-GT2968_2:84945-13202529 RH103_1:84945-13202529 KI-GT2934_1:2387809-13202529 HF0884_1:4669051-13202529 RH131_1:4669051-13202529
ASR16970_2,84945,13202529,DA0000_1:84945-13202529 HF0619_2:84945-13202529 HF0894_2:84945-13202529 KI-GT2968_2:84945-13202529 RH103_1:84945-13202529 KI-GT2934_1:2387809-13202529 HF0884_1:4669051-13202529 RH131_1:4669051-13202529
ASR10434_2,84945,13277230,RH131_1:84945-13277230 HF0884_1:3802315-13277230 DA0000_1:4669051-13277230 HF0619_2:4669051-13277230 HF0894_2:4669051-13277230 KI-GT2934_1:4669051-13277230 KI-GT2968_2:4669051-13277230 RH103_1:4669051-13277230
ASR33932_1,84945,13446565,RH101_2:84945-13446565
ASR07212_2,84945,13604834,AA0000_1:84945-13604834 AE0000_2:84945-13604834 HF0684_2:84945-13604834
ASR13310_2,84945,13604834,AA0000_1:84945-13604834 AE0000_2:84945-13604834 HF0684_2:84945-13604834
ASR19159_2,84945,13604834,AA0000_1:84945-13604834 AE0000_2:84945-13604834 HF0684_2:84945-13604834

* How do I define donor haplotype?
--> donor haplotyp --> the unique combinations of overlapping source haplotypes (third column). For example, in the above input file,
Hap1: HF0078_1 (in the first line of input file)
Hap2: HF0087_2 HF0799_2 KI-GT2934_1 (in the second line)
Hap3: DA0000_1 HF0619_2 HF0894_2 KI-GT2968_2 RH103_1 KI-GT2934_1 HF0884_1 RH131_1 (in the third and fourth line)
...
...

"""

hap_info_d = (
    {}
)  # example --> {"HF0078_1":[{"ASR21337_1":[84945,13008583]}]} # this is a list of dictionary here because it could be that the same combination of source haplotypes could form another non-overlapping haplotype, for instance, like this:
# {"HF0078_1":[{"ASR21337_1":[84945,13008583]},{"ASR21338_2":[14000000,16000000]}]} of course, this will be counted as separate haplotypes

hap_coordinate_d = (
    {}
)  # example --> {"HF0078_1":[[84945,13008583], [14000000,16000000]] }

hap_ss_cord_d = (
    {}
)  # example --> {"HF0078_1":[{"HF0078_1":84945,13008583}], "HF0087_2 HF0799_2 KI-GT2934_1":[{"HF0087_2":[84945,13037346],"HF0799_2":[84945,13037346],"KI-GT2934_1":[84945,13008583]}]}

header = True



with open(sys.argv[1]) as source:
    for line in source:
        if header:
            header = False
        else:
            line = line.rstrip().split(",")
            pattern = re.compile(r"([A-Za-z0-9_-]+):([0-9]+)\-([0-9]+)")
            match = re.findall(pattern, line[3])
            sample_list = [i[0] for i in match]
            cord_list = [list(map(int, list(i[1:]))) for i in match]
            sample_key = " ".join(sample_list)
            dict1 = dict(zip(sample_list, cord_list))
            if sample_key not in hap_coordinate_d:
                hap_coordinate_d[sample_key] = [[int(line[1]), int(line[2])]]
                hap_info_d[sample_key] = [{line[0]: line[1:3]}]
                hap_ss_cord_d[sample_key] = [dict1]
            else:
                is_new_hap = True
                for i, v in enumerate(
                    hap_coordinate_d[sample_key]
                ):  # it is assumed that the same combination of source haplotypes have indeed formed distinct haplotpes
                    if int(line[1]) >= v[0] and int(line[1]) <= v[1]:
                        dict2=hap_ss_cord_d[sample_key][i]
                        is_new_hap, new_dict = merge_overlap_tar_haps(dict2,dict1)
                        if not is_new_hap:
                            max_end = max(v[1], int(line[2]))
                            hap_coordinate_d[sample_key][i][1] = max_end
                            hap_info_d[sample_key][i][line[0]] = line[1:3]
                            hap_ss_cord_d[sample_key][i]=new_dict
                            overlap_idx = i
                            break
                if is_new_hap:
                    hap_coordinate_d[sample_key].append([int(line[1]), int(line[2])])
                    hap_info_d[sample_key].append({line[0]: line[1:3]})
                    hap_ss_cord_d[sample_key].append(dict(zip(sample_list,cord_list)))
                    #print(hap_coordinate_d[sample_key])
                    #print(hap_info_d[sample_key][:2])
                    #print(hap_ss_cord_d[sample_key])

# these dict will be converted to dataframes and be written to separate output files
hap_info_tar_hap = {"hap_id": [], "start": [], "end": [], "target_hap": []}
hap_info_source_hap = {"hap_id": [], "start": [], "end": [], "source_hap": []}
hap_count_dict = {
    "hap_id": [],
    "start": [],
    "end": [],
    "count_of_source_hap": [],
    "count_of_tar_hap": [],
}

# making list of dict so that it can conveniently be looped as the three keys are identical
list_dict = [hap_info_tar_hap, hap_info_source_hap, hap_count_dict]

hap_count = 0

for k in hap_info_d:
    for i, v in enumerate(hap_coordinate_d[k]):
        hap_count += 1
        for idx, val in enumerate(list_dict):
            val["hap_id"].append(f"hap{hap_count}")
            val["start"].append(str(v[0]))
            val["end"].append(str(v[1]))
        ss_info_d = hap_ss_cord_d[k][i]
        ss_info_list = []
        for sample in ss_info_d:
            ss_info_list.append(
                f"{sample}:{ss_info_d[sample][0]}-{ss_info_d[sample][1]}"
            )
        hap_info_source_hap["source_hap"].append(",".join(ss_info_list))
        info_d = hap_info_d[k][i]
        sample_count = 0
        ts_info_list = []
        for ki in info_d:
            sample_count += 1
            ts_info_list.append(f"{ki}:{info_d[ki][0]}-{info_d[ki][1]}")
        hap_info_tar_hap["target_hap"].append(",".join(ts_info_list))
        hap_count_dict["count_of_source_hap"].append(f"{len(k.split())}")
        hap_count_dict["count_of_tar_hap"].append(f"{sample_count}")

list_out = [
    f"{sys.argv[2]}_tar_hap_info.txt",
    f"{sys.argv[2]}_source_hap_info.txt",
    f"{sys.argv[2]}_hap_count_info.txt",
]

for i, v in enumerate(list_dict):
    out_df = pd.DataFrame.from_dict(v)
    out_df = out_df.astype({"start":int,"end":int}).sort_values(["start","end"]).reset_index()
    out_df.index+=1
    out_df.insert(0,"hap_idx","hap"+out_df.index.astype(str))
    out_df = out_df.drop(["hap_id","index"],axis=1)
    out_df.to_csv(list_out[i], index=False, sep="\t")
