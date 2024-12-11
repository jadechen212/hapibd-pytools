#step1 create input files
parallel -j 29 python prepare_input.py Chrom{1}_set_rprh_cpfv_sorted.ibd.gz source_pop_rh.txt recent_pop_fv_neu.txt chrom{1} ::: {1..29}

#step2 merge overlap within each sample
parallel -j 29 python merge_hap.py chrom{1}_target_sample_sorted.txt chrom{1}_pre_hap.csv ::: {1..29}

#step3 infer haplotype
parallel -j 29 python generate_hap_info.py chrom{1}_pre_hap.csv chrom{1} ::: {1..29}
