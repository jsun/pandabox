import os
import sys
import re
import gzip



class VCF:
    '''
    VCF file format, POS with the 1st base having position 1.
    '''
    
    def __init__(self):
        pass
    
    
    
    def parse_vcf(self, file_path, chr_name=None, pos_range=None):
        '''
        Input: /path/to/vcf
        Output: dictionary containing SNPs information. The key is
                a position on the reference, value is a list which
                contains two elements of REF and ALT.
        '''
        
        snp_dict = {}
        
        
        infh = None
        if os.path.splitext(file_path)[1] in ['.gz', '.gzip']:
            infh = gzip.open(file_path, 'rt')
        else:
            infh = open(file_path, 'r')
        
        
        for file_buff in infh:
                
            if file_buff[0] == '#':
                continue
                
            vcf_record = file_buff.replace('\n', '').split('\t')
                
            # discard if not target chromosome
            if chr_name is not None and chr_name != vcf_record[0]:
                continue
                
            # discard if not in the target ranges
            if pos_range is not None and (int(vcf_record[1]) < pos_range[0] or pos_range[1] < int(vcf_record[1])):
                continue
                
            if vcf_record[0] not in snp_dict:
                snp_dict[vcf_record[0]] = []
            
            vcf_tags = {}
            for attr, val in zip(vcf_record[8].split(':'), vcf_record[9].split(':')):
                vcf_tags[attr] = val
                
            snp_dict[vcf_record[0]].append({
                'POS': int(vcf_record[1]),
                'REF': vcf_record[3],
                'ALT': vcf_record[4],
                'QUAL': int(vcf_record[5]),
                'INFO': vcf_tags
            })
        
        infh.close()
        
        
        if len(snp_dict) > 0:
            for chr_name in snp_dict.keys():
                snp_dict[chr_name].sort(key=lambda x: x['POS'])
        
        return snp_dict
    
    
        


if __name__ == '__main__':
    
    vcf = VCF()
    vcf_fpath = '../../datasets/sample.vcf'
    snp_dict = vcf.parse_vcf(vcf_fpath, chr_name='1', pos_range=[500, 1000])
    print(snp_dict)
        





