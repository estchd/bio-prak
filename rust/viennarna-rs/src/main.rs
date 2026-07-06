use std::{ffi::{CStr, CString, c_char}, fs::File, io::{BufRead, BufReader}, ptr::null};

use flate2::read::MultiGzDecoder;
use librna_sys::*;
use rand::{distr::{Alphanumeric, Uniform, uniform::{UniformChar, UniformUsize}}, prelude::*};

fn main() {
    let file_path = "./../data/accessibilities/accessibilities_3utr.gz";

    let file = File::open(file_path).unwrap();

    let gzip_file = MultiGzDecoder::new(file);

    let mut csv_builder = csv::ReaderBuilder::new();

    csv_builder.flexible(true);
    csv_builder.has_headers(false);
    csv_builder.delimiter(b'\t');
    csv_builder.trim(csv::Trim::All);

    let mut csv_file = csv_builder.from_reader(gzip_file);

    for line in csv_file.records().filter_map(|line| line.ok()) {
        let region_name = &line[0];

        let window_size: usize = line[1].parse().unwrap();

        let start: usize = line[2].parse().unwrap();

        let end: usize = line[3].parse().unwrap();

        let modifications: Vec<usize> = line[4]
            .split(',')
            .map(|modification| modification.parse::<usize>().unwrap())
            .collect();

        let footprint: usize = line[5].parse().unwrap();

        let feature: usize = line[6].parse().unwrap();

        let modified = &line[7] == "mod";
        let accessibilities: Vec<f32> = line[8]
            .split(',')
            .map(|accessibilities| accessibilities.parse::<f32>().unwrap())
            .collect();
    }

    println!("done");
}

/*
fn main() {
    let charset = ['A', 'C', 'G', 'U'];

    loop {
        let seq: String = rand::rng()
            .sample_iter(Uniform::try_from(0..charset.len()).unwrap())
            .take(50)
            .map(|index|  charset[index])
            .collect();

        let version: String = VRNA_VERSION.iter().map(|v_char| *v_char as char).collect();

        let c_seq = CString::new(seq.clone()).unwrap();

        let (structure, mfe) = unsafe {
            let ss = vrna_alloc(c_seq.count_bytes() + 1);

            let fc = vrna_fold_compound(c_seq.as_ptr(), null(), VRNA_OPTION_DEFAULT);
            let mfe = vrna_mfe(fc, ss as *mut c_char);

            let safe_ss = CStr::from_ptr(ss as *const c_char);

            let ss_string = safe_ss.to_str().unwrap().to_owned();

            vrna_fold_compound_free(fc);
            free(ss);

            (ss_string, mfe)
        };

        println!("ViennaRNA version is {version}");
        println!("{}", seq);
        println!("{structure} {mfe:6.2}");
    }
}
*/
