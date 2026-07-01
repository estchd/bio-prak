import subprocess
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