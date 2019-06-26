import os
import sys
import re

class Seq:
    
    def __init__(self):
        pass
        
    
    def calc_freq(self, seq, k=1, prob=False):
        """Calculate frequencies of the sequence pattern of k-mer.
        
        Calculate the frequencies of the k-nucleotides or k-amino acids sequence pattern.
        
        Args:
            seq (str): A character of a nucleotide or amino acid sequence.
            k (int): The number of nucleotides or amino acids for calculation.
            prob (bool): if `True`, then return the probabilities instead of frequencies.
        
        
        Returns:
            dict: A dictionary whose keys indicate the k-mer sequence pattern,
                  and the values are the corresponding frequencies or probabilities.
        
        """
        
        seq = seq.upper()
        
        # calculate the total number of k-mer pattenrs
        nt = set()
        for pos in range(len(seq) - k):
            nt.add(seq[pos:(pos + k)])
        
        # create a dictionary to store the frequencies
        freq = {}
        for _nt in nt:
            freq[_nt] = 0
        
        # calculation
        n = 0
        for pos in range(len(seq) - k):
            freq[seq[pos:(pos + k)]] += 1
            n += 1
        
        # calculate the percentages of each letters
        if prob:
            for ptn in freq.keys():
                freq[ptn] = freq[ptn] / n
            
        
        return freq
    
    
    
    
    
    
    
    
    
        
    

