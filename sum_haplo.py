import sys

outprefix = sys.argv[1]
anc_files = sys.argv[2:]

indi_anc = {}
chrom_len = {}
for file in anc_files:
    header = True
    with open(file) as source:
        for line in source:
            line = line.rstrip().split()
            if header:
                chrom_len[line[0]] = int(line[1])
                header = False
            else:
                sample = line[0].split("_")[0]
                if sample not in indi_anc:
                    indi_anc[sample]=0
                indi_anc[sample]+=int(line[1])

with open(f"{outprefix}_proportion_anc.txt","w") as dest:
    total_genome = sum(list(chrom_len.values()))*2
    for sample in indi_anc:
        dest.write(f"{sample} {indi_anc[sample]/total_genome}\n")
