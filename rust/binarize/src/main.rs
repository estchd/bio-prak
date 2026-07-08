#![feature(ptr_cast_slice)]
#![feature(integer_cast_extras)]
#![feature(mpmc_channel)]

use std::{cmp::{max, min}, collections::HashMap, ffi::CString, fs::File, io::Read, os::raw::c_void, path::Path, sync::{mpsc::{Receiver, SyncSender, sync_channel}}, thread::spawn};
use fasta::read::FastaReader;
use flate2::read::MultiGzDecoder;
use librna_sys::*;

use crate::accessibility_file::AccessibilityComputationResult;

mod accessibility_file;

enum PossiblyGzipFile {
    Gzip(MultiGzDecoder<File>),
    Normal(File)
}

impl Read for PossiblyGzipFile {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        match self {
            PossiblyGzipFile::Gzip(multi_gz_decoder) => multi_gz_decoder.read(buf),
            PossiblyGzipFile::Normal(file) => file.read(buf),
        }
    }
}

fn open_possible_gzip_file(file_path: &str) -> PossiblyGzipFile {
    let file = File::open(file_path).unwrap();

    if file_path.ends_with(".gz") {
        let gzip = MultiGzDecoder::new(file);

        PossiblyGzipFile::Gzip(gzip)
    }
    else {
        PossiblyGzipFile::Normal(file)
    }
}

fn main()  {
    let args: Vec<String> = std::env::args().collect();

    let input_path = &args[1];
    let output_path = &args[2];

    println!("Binarizing {input_path} to {output_path}");

    let input_file = open_possible_gzip_file(input_path);

    let output_file = File::create(output_path).unwrap();

    let output_file = MultiGzDecoder::new(output_file);

    let mut csv_builder = csv::ReaderBuilder::new();

    csv_builder.flexible(true);
    csv_builder.has_headers(false);
    csv_builder.delimiter(b'\t');

    let mut csv_reader = csv_builder.from_reader(input_file);

    for record in  csv_reader.records().filter_map(|record| record.ok()) {
        let region_name = &record[0];
        let window_size = &record[1];
        let start = &record[2];
        let end = &record[3];
        let footprint = &record[3];
    }

    println!("Done")
}
