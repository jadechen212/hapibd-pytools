import sys
import pandas as pd

"""
this script will merge the overlapping haplotype of the same individual






"""

def process_df(df):
    new_df_dict = {"fl_hap":[],"start":[],"end":[],"rh_hap":[]}
    tmp_rh_hap = []
    i = 0
    while i<len(df["start"]):
        start_l = df["start"][i]
        end_l = df["end"][i]
        tmp_rh_hap.append(df["source_sample"][i]+"_"+df["ss_hap"][i]+":"+str(start_l)+"-"+str(end_l))
        track_ori_ele = i
        all_window_overlap = True
        for i_n,v_n in enumerate(df["start"][i+1:]):
            track_ori_ele += 1
            if v_n >= start_l and v_n <= end_l:
                tmp_rh_hap.append(df["source_sample"][track_ori_ele]+"_"+df["ss_hap"][track_ori_ele]+":"+str(df["start"][track_ori_ele])+"-"+str(df["end"][track_ori_ele]))
                end_l = max(end_l, df["end"][track_ori_ele])
            else:
                i = track_ori_ele
                all_window_overlap = False
                break
        new_df_dict["fl_hap"].append(df["target_sample"][0]+"_"+df["ts_hap"][0])
        new_df_dict["start"].append(start_l)
        new_df_dict["end"].append(end_l)
        new_df_dict["rh_hap"].append(" ".join(sorted(tmp_rh_hap)))
        del tmp_rh_hap[:]
        if all_window_overlap:
            i=len(df["start"])
    new_df = pd.DataFrame.from_dict(new_df_dict)
    return new_df

def empty_df():
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
    return pd_dict, key_list

with open(sys.argv[1]) as source:
    header = True
    prev_sample = "init"
    pd_dict,key_list = empty_df()
    count = 0
    for line in source:
        if header:
            header = False
        else:
            line = line.rstrip().split(",")
            if line[2]+"_"+line[3] != prev_sample:
                if prev_sample != "init":
                    new_df = pd.DataFrame.from_dict(pd_dict)
                    new_df = new_df.astype({"start":int,"end":int})
                    new_df = process_df(new_df)
                    pd_dict,key_list = empty_df()
                    if count == 0:
                        final_df = new_df.copy()
                    else:
                        final_df = pd.concat([final_df,new_df], ignore_index=True)
                    count += 1
            prev_sample=line[2]+"_"+line[3]
            for i, v in enumerate(line):
                pd_dict[key_list[i]].append(v)

final_df = final_df.sort_values(['start','end'])
final_df.to_csv(f"{sys.argv[2]}",index=False)
