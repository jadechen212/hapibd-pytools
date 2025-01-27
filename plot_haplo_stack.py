import sys
import pandas as pd
from bokeh.plotting import figure, save, output_file
from bokeh.models import Range1d, ColumnDataSource, NumeralTickFormatter
from prepare_df import prepare_df


p = figure(width=1000, height=800)


source_hap_f = sys.argv[1]
num_source_hap = sys.argv[2]
hap_id = sys.argv[3]
tar_hap_f = sys.argv[4]
num_tar_hap = sys.argv[5]
out_prefix = sys.argv[6]

output_file(out_prefix +"_"+hap_id+".html")
p.output_backend = "svg"

df0 = prepare_df(
    source_hap_f,
    hap_id,
    (int(num_source_hap) + int(num_tar_hap)) * 0.1 + 1,
    num_source_hap,
    True,
)
last_idx = list(df0["y_idx"])
last_idx = last_idx[-1]


df1 = prepare_df(tar_hap_f, hap_id, last_idx, num_tar_hap, False)
previous_idx = "none"

df = pd.concat([df0, df1], ignore_index=True)

x_value_list = []
new_list = [[], [], [], []]  # four lists --> coordinates, idx, sample, color
for i, v in enumerate(df["y_idx"]):
    if v != previous_idx:
        if i != 0:
            df_t = {
                "x_values": new_list[0],
                "y_values": new_list[1],
                "sample": new_list[2],
                "colors": new_list[3],
            }
            source = ColumnDataSource(df_t)
            p.multi_line(
                xs="x_values",
                ys="y_values",
                color="colors",
                line_width=2,
                source=source,
            )
            # if new_list[0] not in x_value_list:
            # print(new_list[0])
            # print(df_t)
            # x_value_list.append(new_list[0])
            # p.add_tools(
            #    HoverTool(
            #        show_arrow=False,
            #        line_policy="next",
            #        tooltips=[("sample", "@sample")],
            #    )
            # )
        new_list = [[], [], [], []]  # four lists --> coordinates, idx, sample, color
        previous_idx = v
    new_list[0].append([df["start"][i], df["end"][i]])
    new_list[1].append([float(v), float(v)])
    new_list[2].append(df["sample"][i])
    new_list[3].append(df["color"][i])


p.multi_line(new_list[0], new_list[1], color=new_list[3], line_width=2)
p.y_range = Range1d(0, (int(num_source_hap) + int(num_tar_hap)) * 0.1 + 1 + 0.2)
p.yaxis.visible = False
start = df["start"][0]
end = df["end"][0]
p.x_range = Range1d(start,end)
p.xaxis.major_label_text_font_size = "16px"
p.xaxis[0].formatter = NumeralTickFormatter(format='0.0a')
p.title.text = f"{hap_id} on {out_prefix}:{start}-{end}"
p.title.text_font_size = "20pt"

save(p)
