import sys
import re
import pandas as pd


def prepare_df(hap_f, hap_id, idx, max_hap, is_source):
    df_list = []
    idx = float(idx)
    non_hap_color = "yellow" if is_source else "blue"
    max_hap = int(max_hap)

    with open(hap_f) as source:
        for line in source:
            line = line.rstrip().split()
            if line[0] == hap_id:
                pattern = re.compile(r"([A-Za-z0-9_-]+):([0-9]+)\-([0-9]+)")
                match = re.findall(pattern, line[3])
                ss_hap_dict = {i[0]: int(i[2]) - int(i[1]) for i in match}
                ss_hap_cord_dict = {i[0]: [int(i[1]), int(i[2])] for i in match}
                ss_hap_dict_sorted = dict(
                    sorted(ss_hap_dict.items(), key=lambda item: item[1], reverse=True)
                )
                if is_source:
                    longest_hap_list = [
                        idx,
                        int(line[1]),
                        int(line[2]),
                        line[0],
                        "orange",
                    ]
                    df_list.append(longest_hap_list)
                start_cord = int(line[1])
                end_cord = int(line[2])
                max_sample = (
                    min(len(ss_hap_dict_sorted), max_hap)
                    if is_source
                    else len(ss_hap_dict_sorted) // max_hap
                )
                ss_hap_dict_sorted_subset = (
                    {
                        v: ss_hap_dict_sorted[v]
                        for i, v in enumerate(list(ss_hap_dict_sorted.keys())[:max_sample])
                    }
                    if is_source
                    else {
                        v: ss_hap_dict_sorted[v]
                        for i, v in enumerate(list(ss_hap_dict_sorted.keys())[0::max_sample])
                    }
                )
                for k, v in ss_hap_dict_sorted_subset.items():
                    idx -= 0.1
                    if (
                        ss_hap_cord_dict[k][0] > start_cord
                        and ss_hap_cord_dict[k][1] < end_cord
                    ):
                        list_intersect = [
                            [
                                idx,
                                start_cord,
                                ss_hap_cord_dict[k][0],
                                k,
                                non_hap_color,
                            ],
                            [
                                idx,
                                ss_hap_cord_dict[k][0] + 1,
                                ss_hap_cord_dict[k][1],
                                k,
                                "orange",
                            ],
                            [
                                idx,
                                ss_hap_cord_dict[k][1] + 1,
                                end_cord,
                                k,
                                non_hap_color,
                            ],
                        ]
                    elif (
                        ss_hap_cord_dict[k][0] == start_cord
                        and ss_hap_cord_dict[k][1] < end_cord
                    ):
                        list_intersect = [
                            [
                                idx,
                                ss_hap_cord_dict[k][0],
                                ss_hap_cord_dict[k][1],
                                k,
                                "orange",
                            ],
                            [
                                idx,
                                ss_hap_cord_dict[k][1] + 1,
                                end_cord,
                                k,
                                non_hap_color,
                            ],
                        ]
                    elif (
                        ss_hap_cord_dict[k][0] > start_cord
                        and ss_hap_cord_dict[k][1] == end_cord
                    ):
                        list_intersect = [
                            [
                                idx,
                                start_cord,
                                ss_hap_cord_dict[k][0],
                                k,
                                non_hap_color,
                            ],
                            [
                                idx,
                                ss_hap_cord_dict[k][0] + 1,
                                end_cord,
                                k,
                                "orange",
                            ],
                        ]
                    elif (
                        ss_hap_cord_dict[k][0] == start_cord
                        and ss_hap_cord_dict[k][1] == end_cord
                    ):
                        list_intersect = [[idx, start_cord, end_cord, k, "orange"]]
                    else:
                        print("ERROR: Not possible combination")
                        sys.exit(1)

                    for l in list_intersect:
                        df_list.append(l[:])
    df = pd.DataFrame(df_list, columns=["y_idx", "start", "end", "sample", "color"])

    return df
