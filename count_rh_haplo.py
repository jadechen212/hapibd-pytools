import sys

##read map file
dest = open(sys.argv[3]+"_haplo_count.txt","w")
dest1 = open(sys.argv[3]+"_haplo_fl_info.txt","w")
dest2 = open(sys.argv[3]+"_haplo_rh_info.txt","w")
dest3 = open(sys.argv[3]+"_haplo_link_counts.txt","w")


with open(sys.argv[2]) as map_f:
    for line in map_f:
        line = line.rstrip().split()
        marker_pos = int(line[3])
        marker_pos_dict = {}
        rh_hap_count = 0

        ##dictionary to store rh haplotypes info
        track_rh_hap_dict = {} ## structure is {"hap1":["RHHAP1_1,RHHAP2_2],"hap2":[RHHAP1_2,RHHAP3_1]}
        link_rh_fl_hap_dict = {} ## {"RHHAP1_1":"hap1"} ## this will link rh hap to fleckvieh hap

        ###dictionaries to store fl haplotypes info
        track_fl_hap_dict = {} ## {"hap1":["FLHAP1_1","FLHAP3_1"],"hap2":["FLHAP5_1","FLHAP1_2"]}
        link_fl_rh_hap_dict = {} ## {"FLHAP1_1":"hap1"} this will link fleckvieh hap to rh hap

        with open(sys.argv[1]) as ibd_f:
            for line_i in ibd_f:
                line_i = line_i.rstrip().split()
                fl_h_id = line_i[2]+"_"+line_i[3]
                rh_h_id = line_i[0]+"_"+line_i[1]
                if marker_pos >= int(line_i[5]) and marker_pos <= int(line_i[6]):
                    if rh_hap_count == 0:
                        rh_hap_count += 1
                        track_rh_hap_dict[f"hap{rh_hap_count}"] = [rh_h_id]
                        track_fl_hap_dict[f"hap{rh_hap_count}"] = [fl_h_id]
                        link_fl_rh_hap_dict[fl_h_id] = f"hap{rh_hap_count}"
                        link_rh_fl_hap_dict[rh_h_id] = f"hap{rh_hap_count}"
                    else:
                        if fl_h_id in link_fl_rh_hap_dict:
                            if rh_h_id not in link_rh_fl_hap_dict:
                                    track_rh_hap_dict[link_fl_rh_hap_dict[fl_h_id]].append(rh_h_id)
                                    link_rh_fl_hap_dict[rh_h_id] = link_fl_rh_hap_dict[fl_h_id]
                        else:
                            if rh_h_id in link_rh_fl_hap_dict:
                                link_fl_rh_hap_dict[fl_h_id]=link_rh_fl_hap_dict[rh_h_id]
                                if fl_h_id in track_fl_hap_dict[link_rh_fl_hap_dict[rh_h_id]]:
                                    print(f"this is unxpected, check {line_i}")
                                    sys.exit(1)
                                else:
                                    track_fl_hap_dict[link_rh_fl_hap_dict[rh_h_id]].append(fl_h_id)
                            else:
                                rh_hap_count += 1
                                track_rh_hap_dict[f"hap{rh_hap_count}"] = [rh_h_id]
                                track_fl_hap_dict[f"hap{rh_hap_count}"] = [fl_h_id]
                                link_fl_rh_hap_dict[fl_h_id] = f"hap{rh_hap_count}"
                                link_rh_fl_hap_dict[rh_h_id] = f"hap{rh_hap_count}"
            dest.write(f"{marker_pos}\t{len(track_rh_hap_dict)}")
            dest1.write(f"{marker_pos}\t")
            dest2.write(f"{marker_pos}\t")
            dest3.write(f"{marker_pos}\t")
            num_fl_hap = 0
            for hap in track_rh_hap_dict:
                num_fl_hap += len(track_fl_hap_dict[hap])
                dest1.write(hap+"\t"+"\t".join(track_fl_hap_dict[hap])+"\t")
                dest3.write(hap+"\t"+str(len(track_fl_hap_dict[hap]))+"\t")
                dest2.write(hap+"\t"+"\t".join(track_rh_hap_dict[hap])+"\t")
            dest.write(f"\t{num_fl_hap}\n")
            dest1.write("\n")
            dest3.write("\n")
            dest2.write("\n")
