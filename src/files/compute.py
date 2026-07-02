import subprocess
import gzip
import csv
from pathlib import Path 

def download_fna(prerequisites, output_path, multiple_outputs):
    fna_url = "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz"
    
    print("Downloading fna")
    
    with open(output_path, "tw") as outputFile:
        wget = subprocess.Popen(('wget', "-q", "-O-", fna_url), stdout=outputFile)

        wget.wait()

    print("Downloading fna done")

def download_gtf(prerequisites, output_path, multiple_outputs):
    gtf_url = "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.gtf.gz"

    print("Downloading gtf")
    
    with open(output_path, "tw") as outputFile:
        wget = subprocess.Popen(('wget', "-q", "-O-", gtf_url), stdout=outputFile)

        wget.wait()

    print("Downloading gtf done")

def download_m6A(prerequisites, output_path, multiple_outputs):
    m6A_url = "http://bioinformaticsscience.cn/rmbase/download/modSingleSiteFiles/hg38/hg38.m6A.tar.gz?genome=hg38&modtype=m6A"

    print("Downloading m6A")
    
    with open(output_path, "tw") as outputFile:
        wget = subprocess.Popen(('wget', "-q", "-O-", m6A_url), stdout=subprocess.PIPE)
        tar = subprocess.Popen(('tar', "-xz", "-O"), stdin=wget.stdout, stdout=subprocess.PIPE) 
        gzip = subprocess.Popen(("gzip", "-c"), stdin=tar.stdout, stdout=outputFile)
    
        wget.wait()
        tar.wait()
        gzip.wait()

    print("Downloading m6A done")

def copy_file(prerequisites, output_path, multiple_outputs):
    input_path = prerequisites[0].get_possibly_gzip_path()
    
    print("Copying", input_path, "to", output_path)
    
    subprocess.run(["cp", input_path, output_path])
    
    print("Copying", input_path, "to", output_path, "done")

def filter_fna(prerequisites, outputPath, multiple_outputs):
    input_path = prerequisites[0].get_possibly_gzip_path()
    
    print("Filtering fna", input_path, "to", outputPath)

    with open(outputPath, "tw") as outputFile:
        zcat = subprocess.Popen(('zcat', input_path), stdout=subprocess.PIPE)
        sed = subprocess.Popen(('sed', "-n", "/>NC_000008.11/,/>/p"), stdin=zcat.stdout, stdout=subprocess.PIPE)   
        head = subprocess.Popen(('head', "-n", "-1"), stdin=sed.stdout, stdout=subprocess.PIPE) 
        gzip = subprocess.Popen(('gzip', "-c"), stdin=head.stdout, stdout=outputFile)
        
        zcat.wait()
        sed.wait()
        head.wait()
        gzip.wait()

    print("Filtering fna", input_path, "to", outputPath, "done")

def filter_gtf(prerequisites, outputPath, multiple_outputs):
    input_path = prerequisites[0].get_possibly_gzip_path()
    
    print("Filtering gtf", input_path, "to", outputPath)
    
    with open(outputPath, "tw") as outputFile:
        zcat = subprocess.Popen(('zcat', input_path), stdout=subprocess.PIPE)
        grep = subprocess.Popen(('grep', "NC_000008.11"), stdin=zcat.stdout, stdout=subprocess.PIPE)   
        gzip = subprocess.Popen(('gzip', "-c"), stdin=grep.stdout, stdout=outputFile)
        
        zcat.wait()
        grep.wait()
        gzip.wait()

    print("Filtering gtf", input_path, "to", outputPath, "done")

def filter_bed(prerequisites, outputPath, multiple_outputs):
    input_path = prerequisites[0].get_possibly_gzip_path()
    
    print("Filtering bed", input_path, "to", outputPath)

    with open(outputPath, "tw") as outputFile:
        zcat = subprocess.Popen(('zcat', input_path), stdout=subprocess.PIPE)
        grep = subprocess.Popen(('grep', "chr8"), stdin=zcat.stdout, stdout=subprocess.PIPE)   
        gzip = subprocess.Popen(('gzip', "-c"), stdin=grep.stdout, stdout=outputFile)

        zcat.wait()
        grep.wait()
        gzip.wait()

    print("Filtering bed", input_path, "to", outputPath, "done")
        
def rename_fna(prerequisites, outputPath, multiple_outputs):
    input_path = prerequisites[0].get_possibly_gzip_path()
    
    print("Renaming fna", input_path, "to", outputPath)

    with open(outputPath, "tw") as outputFile:
        zcat = subprocess.Popen(('zcat', input_path), stdout=subprocess.PIPE)
        sed = subprocess.Popen(('sed', "s/>NC_000008.11/>chr8/g"), stdin=zcat.stdout, stdout=subprocess.PIPE)   
        gzip = subprocess.Popen(('gzip', "-c"), stdin=sed.stdout, stdout=outputFile)
        
        zcat.wait()
        sed.wait()
        gzip.wait()

    print("Renaming fna", input_path, "to", outputPath, "done")
    
def rename_gtf(prerequisites, outputPath, multiple_outputs):
    input_path = prerequisites[0].get_possibly_gzip_path()
    
    print("Renaming gtf", input_path, "to", outputPath)
    
    with open(outputPath, "tw") as outputFile:
        zcat = subprocess.Popen(('zcat', input_path), stdout=subprocess.PIPE)
        sed = subprocess.Popen(('sed', "s/NC_000008.11/chr8/g"), stdin=zcat.stdout, stdout=subprocess.PIPE)   
        gzip = subprocess.Popen(('gzip', "-c"), stdin=sed.stdout, stdout=outputFile)
        
        zcat.wait()
        sed.wait()
        gzip.wait()
    
    print("Renaming gtf", input_path, "to", outputPath, "done")

def bgzip_file(prerequisites, outputPath, multiple_outputs):
    input_path = prerequisites[0].get_possibly_gzip_path()
    
    print("Bgzipping", input_path, "to", outputPath)
    
    with open(outputPath, "tw") as outputFile:
        zcat = subprocess.Popen(('zcat', input_path), stdout=subprocess.PIPE) 
        bgzip = subprocess.Popen(('bgzip', "-c"), stdin=zcat.stdout, stdout=outputFile)
        
        zcat.wait()
        bgzip.wait()
        
    print("Bgzipping", input_path, "to", outputPath, "done")

def assemble_regions(prerequisites, outputPath, multiple_outputs):
    input_path = prerequisites[0].get_possibly_gzip_path()
    
    print("Assembling regions")

    outputTemplate = str(Path(outputPath).parent) + "/region"
    
    subprocess.run(("python", "software/extract-transcript-regions/extract_transcript_regions.py", "--gtf", "-i", input_path, "-o", outputTemplate))

    for multiple_output in multiple_outputs:
        multiple_output_file = multiple_output()

        if not multiple_output_file.file_exists():
            print("Path was:", multiple_output_file.get_possibly_gzip_path())
            raise Exception("region extraction did not generate all files")

        file_hash = multiple_output_file.get_computed_file_hash()

        multiple_output_file.save_file_hash(file_hash)
                   
    print("Assembling regions done")

def get_region_fasta(prerequisites, outputPath, multiple_outputs):
    bgzipped_path = prerequisites[0].get_possibly_gzip_path()
    input_path = prerequisites[1].get_possibly_gzip_path()

    print("Getting fasta for", input_path, "into", outputPath)
    
    with open(outputPath, "tw") as outputFile:
        bedtools = subprocess.Popen(("bedtools", "getfasta", "-s", "-split", "-fi", bgzipped_path, "-bed", input_path, "-name"), stdout=subprocess.PIPE)
        gzip = subprocess.Popen(("gzip", "-c"), stdin=bedtools.stdout, stdout=outputFile)

        bedtools.wait()
        gzip.wait()
    
    print("Getting fasta for", input_path, "into", outputPath, "done")

def intersect_region_modifications(prerequisites, outputPath, multiple_outputs):
    renamed_path = prerequisites[0].get_possibly_gzip_path()
    input_path = prerequisites[1].get_possibly_gzip_path()
    
    print("Computing Intersects for", input_path, "into", outputPath)

    with open(outputPath, "tw") as outputFile:
        bedtools = subprocess.Popen(["intersectBed", "-a", input_path, "-b", renamed_path, "-s", "-split"], stdout=subprocess.PIPE)
        gzip = subprocess.Popen(["gzip", "-c"], stdin=bedtools.stdout, stdout=outputFile)

        bedtools.wait()
        gzip.wait()

    print("Computing Intersects for", input_path, "into", outputPath, "done")

def make_local_modifications(prerequisites, outputFile, multiple_outputs):
    inputFile = prerequisites[0].get_possibly_gzip_path()
    
    print("Converting intersects in", inputFile, "into local intersects in", outputFile)
    
    with gzip.open(inputFile, "rt") as inputStream:
        with gzip.open(outputFile, "wt") as outputStream:
            csv_reader = csv.reader(inputStream, delimiter="\t", quotechar='"')
            csv_writer = csv.writer(outputStream, delimiter="\t", quotechar='"')
            
            for row in csv_reader:
                identifier = row[3]
                m6A_pos_global = int(row[2]) #- int(row[1])
                feature_start = int(row[6])
                feature_end = int(row[7])
                feature_strand = row[5]
                num_blocks = int(row[9])
                block_sizes = row[10].split(",")
                block_starts = row[11].split(",")
    
                # remove empty last element from block lists
                if block_sizes[-1] == '':
                    block_sizes.pop()
                if block_starts[-1] == '':
                    block_starts.pop()
                # convert block data into actual integer numbers
                block_sizes = [ int(v) for v in block_sizes ]
                block_starts = [ int(v) for v in block_starts ]
    
                # compute length of blocks, i.e. length of feature after splicing
                l = sum(block_sizes)
                identifier += "(" + feature_strand + ")"
    
                # everything is easy and straight-forward if we have a single block
                if num_blocks == 1:
                    m6A_pos_local = m6A_pos_global - feature_start
                else:
                    if num_blocks != len(block_starts) or \
                       num_blocks != len(block_sizes):
                        #print('something fishy', num_blocks, len(block_sizes), len(block_starts))
                        # bedtools 2.30.0 seems to truncate long lines in intersect, so sometimes data is weird or missing
                        # skip those entries for now!
                        continue
    
                    # for multilple blocks, we need to go through all of them until we find the correct position
                    # first, find out relative (local) coordinate within unspliced transcript
                    m6A_pos_local = m6A_pos_global - feature_start
                    # next, we need to substract all positions that are spliced out when the blocks are concatenated
                    # for that let us count the number of nucleotides spliced out between the blocks before
                    spliced_nt = 0
                    for i, start in enumerate(block_starts[1:], start = 1):
                        if m6A_pos_local < start:
                            #print(f'found {m6A_pos_global} between {feature_start + block_starts[i-1]} and {feature_start + block_starts[i - 1] + block_sizes[i - 1]}')
                            #print(f'next block at {feature_start + block_starts[i] + 1}')
                            break # found the block
                        else:
                            spliced_nt += block_starts[i] - block_starts[i - 1] - block_sizes[i - 1]
                    
                    m6A_pos_local -= spliced_nt # now we have local position from left side, i.e. start for + and end for - strand
    
                # swap coordinates for negative strand
                if feature_strand == "-":
                    #print(m6A_pos_local, spliced_nt)
                    m6A_pos_local = l - m6A_pos_local + 1
                    
                    csv_writer.writerow([row[3], m6A_pos_local - 1, m6A_pos_local])
    
    print("Converting intersects in", inputFile, "into local intersects in", outputFile, "done")

class AssembledRegion:
    def __init__(self, regionName):
        self.name = regionName
        self.modifications = []

def assemble_local_modifications(prerequisites, output_path, multiple_outputs):
    input_path = prerequisites[0].get_possibly_gzip_path()
    
    print("Assembling local Intersects for", input_path, "into", output_path)

    regions = {}

    with gzip.open(input_path, "rt") as inputFile:
        reader = csv.reader(inputFile, delimiter="\t")

        for line in reader:
            region_name = line[0]
            position = int(line[1])

            if not region_name in regions.keys():
                regions[region_name] = AssembledRegion(region_name)

            regions[region_name].modifications.append(position)

    for key in regions.keys():
        regions[key].modifications.sort()

    with gzip.open(output_path, "wt") as outputFile:
        writer = csv.writer(outputFile, delimiter="\t")

        for key in regions.keys():
            
            writer.writerow([regions[key].name, ",".join(map(str, regions[key].modifications))])
    
    print("Assembling local Intersects for", input_path, "into", output_path, "done")
