def merge_overlap_tar_haps(dict1, dict2):
    new_dict = {}
    is_new_hap = False
    for sample in dict1:
        # print(hap_ss_cord_d[sample_key])
        old_cords = dict1[sample]
        new_cords = dict2[sample]
        if old_cords[0] not in range(new_cords[0], new_cords[1]) and new_cords[
            0
        ] not in range(old_cords[0], old_cords[1]):
            is_new_hap = True
        new_dict[sample] = [
            min(old_cords[0], new_cords[0]),
            max(old_cords[1], new_cords[1]),
        ]
    return is_new_hap, new_dict
