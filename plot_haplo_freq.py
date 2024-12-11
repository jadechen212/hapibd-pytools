import sys
import re
from bokeh.models import HoverTool, ColumnDataSource, Legend
from bokeh.plotting import figure, save, output_file, show
from bokeh.palettes import Category20
import bokeh.layouts

hap_info_f = sys.argv[1]
hap_source_f = sys.argv[2]
map_f = sys.argv[3]
out_f = sys.argv[4]

snp_hap_dict = {}

count_hap_dict = {}

header = True

def read_source_hap(hap_list):
    header = True
    hap_dict_list = [{},{},{}]
    for hap in hap_list:
        for dict_v in hap_dict_list:
            dict_v[hap]=[]
    with open(hap_source_f) as source:
        for line in source:
            if header:
                header = False
            else:
                line = line.rstrip().split()
                if line[0] in hap_list:
                    hap_dict_list[0][line[0]] = line[1] # this dict contains info about start
                    hap_dict_list[1][line[0]] = line[2] # this dict contains info about end
                    pattern = re.compile(r"([A-Za-z0-9_-]+):([0-9]+)\-([0-9]+)")
                    match = re.findall(pattern, line[3])
                    ss_hap_dict = {i[0]:int(i[2])-int(i[1]) for i in match}
                    ss_hap_dict_sorted =  dict(sorted(ss_hap_dict.items(), key=lambda item: item[1], reverse=True))
                    min_slice = min(len(ss_hap_dict_sorted),5)
                    hap_dict_list[2][line[0]] = ",".join(list(ss_hap_dict_sorted.keys())[:min_slice]) # this dict contains most important source haplo
    return hap_dict_list

with open(out_f,"w") as dest:
    with open(map_f) as source:
        for line_f in source:
            line_f = line_f.rstrip().split()
            snp_pos = int(line_f[3])
            snp_hap_dict[snp_pos]={}
            header = True
            with open(hap_info_f) as source1:
                for line in source1:
                    if header:
                        header = False
                    else:
                        line = line.rstrip().split("\t")
                        if int(line[1]) <= snp_pos and int(line[2]) >= snp_pos:
                            pattern = re.compile(r"([A-Za-z0-9_-]+):([0-9]+)\-([0-9]+)")
                            match = re.findall(pattern, line[3])
                            sample_list = [i[0] for i in match]
                            cord_list = [list(map(int, list(i[1:]))) for i in match]
                            sample_cord_dict = dict(zip(sample_list, cord_list))
                            for sample in sample_cord_dict:
                                if sample_cord_dict[sample][0] <= snp_pos and sample_cord_dict[sample][1] >= snp_pos:
                                    if line[0] not in snp_hap_dict[snp_pos]:
                                        snp_hap_dict[snp_pos][line[0]] = 0
                                    snp_hap_dict[snp_pos][line[0]] += 1
                        elif int(line[1]) > snp_pos:
                            break
            hap_dict = snp_hap_dict[snp_pos]
            count_hap_dict[snp_pos] = sum(list(hap_dict.values()))

sorted_count_hap_dict = dict(sorted(count_hap_dict.items(), key=lambda item: item[1], reverse=True))
bar_plot_dict = snp_hap_dict[list(sorted_count_hap_dict.keys())[0]]
total_count = sorted_count_hap_dict[list(sorted_count_hap_dict.keys())[0]]
sorted_bar_plot_dict = dict(sorted(bar_plot_dict.items(), key=lambda item: item[1], reverse=True))

sorted_bar_plot_dict_perc = {k:v/total_count*100 for(k,v) in sorted_bar_plot_dict.items()}

haps = list(sorted_bar_plot_dict_perc.keys())[:20]
counts = list(sorted_bar_plot_dict_perc.values())[:20]

hap_dict_list = read_source_hap(hap_list=haps)

starts = list(hap_dict_list[0].values())
ends = list(hap_dict_list[1].values())
source = list(hap_dict_list[2].values())


source = ColumnDataSource(data=dict(haps=haps,counts=counts, color=list(Category20[20]),starts=starts,ends=ends,source=source))

p=figure(x_range=haps,height=650,width=1000,title="hap counts")

output_file(f"{out_f}.html")

p.output_backend = "svg"

p.vbar(x="haps",top="counts",width=0.9,color="color", legend_field="haps",source=source)

p.xgrid.grid_line_color=None

p.add_tools(HoverTool(tooltips=[("start", "@starts"), ("end", "@ends"),("source","@source")]))

p.yaxis.axis_label="% of haplotypes"

p.title = f"Total number of FL haps in IBD with RH haps on {out_f} at position {snp_pos}:{total_count} "

save(p)
