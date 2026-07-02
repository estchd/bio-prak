import random
import gzip
import csv

def randseq(l):
    """ Returns a random sequence of length l. """
    rseq = []
    for _ in range(l):
       rseq.append(random.choice('ACGU'))
    return ''.join(rseq)

class AssembledRegion:
    def __init__(self, regionName):
        self.name = regionName
        self.modifications = []
        
def load_region_modifications(inputFile):
    regions = {}
    
    with inputFile.open_or_recompute() as inputFile:
        reader = csv.reader(inputFile, delimiter="\t")

        for line in reader:
            region_name = line[0]
            modifications = list(map(int, line[1].split(",")))
            region = AssembledRegion(region_name)
            region.modifications = modifications
            regions[region_name] = region

    return regions