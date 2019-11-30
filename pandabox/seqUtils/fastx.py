import os
import sys
import re

class FASTX:
    
    def __init__(self):
        pass
        
    
    def parse_fasta(self, file_path):
        """Parse FASTA file.
        
        Open the given FASTA file and read entries one by one,
        return as an iterator.
        
        Args:
            file_path (str): A file path to FASTA file.
        
        Returns:
            iterator: An iterator which contains a dictionary,
                      and the dictionary contains squence ID and sequence.
        
        """
        
        entry_id = None
        entry_seq = None
        
        with open(file_path, 'r') as infh:
            for file_buff in infh:
                file_buff = file_buff.replace('\n', '')
                
                # entry header
                if file_buff[0:1] == '>':
                    
                    # return the previous entry
                    if entry_id is not None and entry_seq is not None:
                        yield {'id': entry_id, 'seq': entry_seq}
                    
                    entry_id = file_buff[1:]
                    entry_seq = None
                
                # entry sequence
                else:
                    if entry_seq is None:
                        entry_seq = ''
                    entry_seq = entry_seq + file_buff
        
        # return the last entry
        yield {'id': entry_id, 'seq': entry_seq}
                
    
    
    
    def parse_fastq(self, file_path):
        """Parse FASTQ file.
        
        Open the given FASTQ file and read entries one by one,
        return as an iterator.
        
        Args:
            file_path (str): A file path to FASTQ file.
        
        Returns:
            iterator: An iterator which contains a dictionary,
                      and the dictionary contains squence ID and sequence,
                      and quality.
        
        """
        
        with open(file_path, 'r') as infh:
            
            # 1 for header, 2 for sequence, 3 for header, 4 for quality
            i = 0
            
            entry_id = None
            entry_seq = None
            entry_qual = None
            
            for file_buff in infh:
                i = i + 1
                
                file_buff = file_buff.replace('\n', '')
                
                if i == 1:
                    entry_id = file_buff[1:]
                elif i == 2:
                    entry_seq = file_buff
                elif i == 3:
                    pass
                elif i == 4:
                    entry_qual = file_buff
                    
                    yield {'id': entry_id, 'seq': entry_seq, 'quality': entry_qual}
                    
                    entry_id = None
                    entry_seq = None
                    entry_qual = None
    
    
    
