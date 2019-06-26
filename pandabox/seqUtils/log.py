import os
import sys
import re

class LogFile:
    
    def __init__(self):
        pass
    
    
    
    def parse_star_log(self, file_path):
        '''Parse STAR-aligner log file.
        
        STAR aligner outputs the final log file (*.Log.final.out).
        This function is used for parsing the final log file,
        and outputs the mapped rates with TSV format.
        
        Args:
            file_path (str): A file path to log file.
        
        Returns:
            list: A list contains file path, name, mapped reads,
                  multiple loci, and too many loci reads.
        '''
        
        uniq_r = ''
        multi_r = ''
        much_r = ''

        with open(file_path, 'r') as infh:

            for buf in infh:
                buf = buf.replace('\n', '')

                if 'Uniquely mapped reads %' in buf:
                    buf_records = buf.split('\t')
                    uniq_r = buf_records[1].replace('%', '')

                if '% of reads mapped to multiple loci' in buf:
                    buf_records = buf.split('\t')
                    multi_r = buf_records[1].replace('%', '')

                if '% of reads mapped to too many loci' in buf:
                    buf_records = buf.split('\t')
                    much_r = buf_records[1].replace('%', '')

        file_name = os.path.basename(file_path)
        return [file_path, file_name, uniq_r, multi_r, much_r]
        
        
        
        
        
