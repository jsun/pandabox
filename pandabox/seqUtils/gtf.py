import os
import sys
import re
import gzip


class GTF:
    
    def __init__(self):
        pass
    
    
    
    def parse_gtf(self, file_path, feature_type='gene', feature_idtag='gene_id', feature_id=None, output_fmt=3):
        '''
        Input: /path/to/gtf
        Output: dictionary containing lists of gene annotations.
                the chromosome name/number is set as dictionary keys,
                and value is set as lists of gene annotations.
        
        '''
        
        gene_ranges = {}
        
       

        infh = None
        if os.path.splitext(file_path)[1] in ['.gz', '.gzip']:
            infh = gzip.open(file_path, 'rt')
        else:
            infh = open(file_path, 'r')
        

        # check format (GTF or GFF) and set the regex pattern
        file_path_wihtoutgz = re.sub('\.gz$|\.gzip$', '', file_path)
        if os.path.splitext(file_path_wihtoutgz)[1] == '.gtf':
            geneid_pattern = re.compile(feature_idtag + ' "([^"]+)";')
        else:
            geneid_pattern = re.compile(feature_idtag + ':([^:;]+);')
        
        
        for file_buff in infh:
            gtf_record = file_buff.replace('\n', '').split('\t')
            if len(gtf_record) < 9:
                continue
                
            # only search the specified feature type
            if gtf_record[2] == feature_type:
                    
                # find feature id (gene id, exon id, etc...)
                m = geneid_pattern.search(gtf_record[8])
                if m:
                    fid = m.group(1)
                        
                    if feature_id is not None and feature_id != fid:
                        continue
                        
                        
                    # add record if every conditions are satisfied
                    if gtf_record[0] not in gene_ranges:
                        gene_ranges[gtf_record[0]] = []
    
                    if output_fmt == 3:
                        gene_ranges[gtf_record[0]].append([fid, int(gtf_record[3]), int(gtf_record[4])])
                    elif output_fmt == 2:
                        gene_ranges[gtf_record[0]].append([int(gtf_record[3]), int(gtf_record[4])])
                    else:
                        raise ValueError('Only 2 or 3 can be set in `output_fmt` argument.')
                
        infh.close()
                
        return gene_ranges
    
    
    
    
    
    def calc_cdna_len(self, gff_file, attr_pattern):
        ## Description:
        ##   Calculation of non-overlapping exon length with GFF file for each gene.
        ## 
        ##   e.g) Gene G has four transcripts: Ga, Gb, Gc, and Gd. The four transcripts
        ##        have different numbers of exons and different combinations of exons.
        ##        Some regions are shared with the four transcripts, and some regions
        ##        are only used by a single transcript. These information are saved in
        ##        GTF file. This script is used for calculating the non-overlapping
        ##       exon (cDNA) length with GFF file.
        ## 
        ##    transcript Ga     ========-----==============-------============= 
        ##    transcript Gb     ========-----==============
        ##    transcript Gc     ========--------------------------=============
        ##    transcript Gd     ========--------------==========--=============
        ##    
        ##    cDNA              ========     ===================  =============
        ##
        ## Usage:
        ##
        ##   python calc_cdna_len.py gene_id ath.gtf > cds_length.txt
        ##
        ##     gene_id: 'gene_id' can be changed to 'transcript_id', or 'gene_name'
        ##              according your purpose and your GTF file.
        ##
        ##     ath.gtf: File path to the GTF file.
        ## 


        #
        # Calculate the length of non-overlapping exons for each gene.
        #
        idptn = re.compile(attr_pattern + ' "([^"]+)";')
        gene_length = {}
        
        
        gfffh = None
        if os.path.splitext(gff_path)[1] in ['.gz', '.gzip']:
            gfffh = gzip.open(file_path, 'rt')
        else:
            gfffh = open(file_path, 'r')
        
        # save the coordinates of the positions of all exons.
        for buf in gfffh:
            if buf[0:1] == '#':
                continue
            buf_records = buf.split('\t')
            if buf_records[2] == 'exon':
                mat = idptn.search(buf_records[8])
                if mat:
                    gene_name = mat.group(1)
                    if gene_name not in gene_length:
                        gene_length[gene_name] = []
                    gene_length[gene_name].append([int(buf_records[3]), int(buf_records[4])])
        
        gfffh.close()
        
        # find the maximum and minimum coodinates of the position of exons for each gene.
        gene_length_max = {}
        gene_length_min = {}
        for gene_name in gene_length.keys():
            for exon_range in gene_length[gene_name]:
                # define
                if gene_name not in gene_length_max:
                    gene_length_max[gene_name] = max(exon_range)
                if gene_name not in gene_length_min:
                    gene_length_min[gene_name] = min(exon_range)
                # update
                if max(exon_range) > gene_length_max[gene_name]:
                    gene_length_max[gene_name] = max(exon_range)
                if min(exon_range) < gene_length_min[gene_name]:
                    gene_length_min[gene_name] = min(exon_range)
    
        # generate an list contained 0 or 1 for each gene.
        # '0' means that the position did not become a exon region,
        # '1' means that the position became a exon region at least once.
        gene_length_bits = {}
        for gene_name in gene_length.keys():
            if gene_name not in gene_length_bits:
                gene_length_bits[gene_name] = [0] * (gene_length_max[gene_name] - gene_length_min[gene_name] + 1)
            for exon_range in gene_length[gene_name]:
                for i in range(min(exon_range), max(exon_range) + 1):
                    pos_i = i - gene_length_min[gene_name]
                    gene_length_bits[gene_name][pos_i] = 1
    
        # calculate the total values of the list contained 0 or 1.
        gene_length_final = {}
        for gene_name in gene_length.keys():
            gene_length_final[gene_name] = sum(gene_length_bits[gene_name])

        return gene_length_final

    
    
    
    
    
    
    def calc_nonoverlap_region(self, regions_1, regions_2):
        '''
        Input:
            regions_1 = [[0, 10], [22, 40], [120, 140], [240, 290], [320, 350], [360, 370]]
            regions_2 = [[0, 12], [22, 40], [130, 145], [220, 280], [310, 360]]
        '''
        
        
        def _merge_regions(regions_1, regions_2):
            regions = regions_1
        
            for i, region in enumerate(regions):
                for j, region_2 in enumerate(regions_2):
                    
                    if i < len(regions) - 1 and regions[i+1][1] < region_2[0]:
                        break
                    if i > 0 and region_2[1] < regions[i-1][0]:
                        continue
                    # if the two elements has the overlap
                    # case 1:
                    #    ref   --------------------
                    #    alt         ------------------------
                    #
                    # case 2:
                    #    ref          --------------------
                    #    alt   ------------------------
                    #
                    # case 3:
                    #    ref   --------------------------------
                    #    alt         -------------------
                    #
                    # case 4:
                    #    ref         --------------
                    #    alt   -----------------------------
                    #
                    # case 5:
                    #    ref                         --------
                    #    alt   ------- (first) 
                    #
                    # case 6:
                    #    ref   ---------              --------
                    #    alt              -------  (interval)
                    #
                    # case 7:
                    #    ref   --------- 
                    #    alt                  ------- (last)
                    #
                    is_case1 = region[0] <= region_2[0] and region_2[0] <= region[1]
                    is_case2 = region[0] <= region_2[1] and region_2[1] <= region[1]
                    is_case3 = region[0] <= region_2[0] and region_2[1] <= region[1]
                    is_case4 = region_2[0] <= region[0] and region[1] <= region_2[1]
                    is_case5 = False
                    is_case6 = False
                    is_case7 = False
                    if i == 0:
                        is_case5 = region_2[0] < region[0] and region_2[1] < region[0]
                    elif i == len(regions) - 1:
                        is_case7 = region[0] < region_2[0] and region[1] < region_2[0]
                    else:
                        is_case6 = regions[i-1][1] < region_2[0] and region_2[1] < regions[i][0]
                    
                    if is_case1 or is_case2 or is_case3 or is_case4:
                        # update the 5'-end
                        if region[0] <= region_2[0]:
                            pass
                        else:
                            region[0] = region_2[0]
                    
                        # update the 3'-end
                        if region[1] <= region_2[1]:
                            region[1] = region_2[1]
                        else:
                            pass
                    
                    elif is_case5 or is_case6 or is_case7:
                        regions.append(region_2)
                    
                    
                    
                
            regions = set([tuple(r) for r in regions])
            regions = [list(r) for r in regions]
            regions.sort()
            
            return regions
        
        regions = _merge_regions(regions_1, regions_2)
        regions = _merge_regions(regions, regions)
        
        return regions
        
        


if __name__ == '__main__':
    
    gtf = GTF()
    cov = gtf.calc_nonoverlap_region([[0, 10], [22, 40], [120, 140], [190, 200],
                                      [240, 290], [320, 350], [360, 370]],
                                     [[0, 12], [22, 40], [130, 145], [160, 180],
                                      [220, 280], [310, 360]])
    print(cov)
    
    cov = gtf.calc_nonoverlap_region([[110, 140], [180, 190], [220, 260]],
                                     [[30, 50], [90, 210], [240, 280], [290, 310]])
    print(cov)
        
    cov = gtf.calc_nonoverlap_region([[110, 140], [180, 190], [220, 260], [400, 420]],
                                     [[30, 50], [90, 210], [240, 280], [290, 310]])
    print(cov)
        
        
        





