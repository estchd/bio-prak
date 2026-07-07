#![feature(ptr_cast_slice)]
#![feature(integer_cast_extras)]

use std::{cmp::{max, min}, collections::HashMap, ffi::{CStr, CString, c_char}, fs::File, io::{BufRead, BufReader, Read}, os::raw::c_void, path::Path, ptr::null};
use fasta::read::FastaReader;
use rayon::prelude::*;
use flate2::read::MultiGzDecoder;
use librna_sys::*;
use rand::{distr::{Alphanumeric, Uniform, uniform::{UniformChar, UniformUsize}}, prelude::*};

fn get_naive_start(modification: isize, window_size: isize) -> isize {
    modification - window_size
}

fn get_naive_end(modification: isize, window_size: isize) -> isize {
    modification + window_size
}

struct Interval {
    start: isize,
    end: isize,
    modifications: Vec<isize>
}

fn get_interval_from_modification(modification: isize, window_size: isize, sequence_length: isize) -> Interval {
    let interval_start = max(0, get_naive_start(modification, window_size));
    let interval_end = min(sequence_length, get_naive_end(modification, window_size));

    Interval {
        start: interval_start,
        end: interval_end,
       modifications: vec![modification]
    }
}

fn are_intervals_overlapping(a: &Interval, b: &Interval) -> bool {
    a.end >= b.start || b.end >= a.start
}

fn combine_intervals(a: &Interval, b: &Interval) -> Interval {
    let combined_modifications = a.modifications.iter().chain(b.modifications.iter()).copied().collect();

    Interval {
        start: min(a.start, b.start),
        end: max(a.end, b.end),
        modifications: combined_modifications,
    }
}

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

struct AssembledRegion {
    modifications: Vec<isize>
}

fn load_region_modifications(input_file_path: &str) -> HashMap<String, AssembledRegion> {
    let mut regions: HashMap<String, AssembledRegion> = HashMap::new();

    let file = open_possible_gzip_file(input_file_path);

    let mut csv_builder = csv::ReaderBuilder::new();

    csv_builder.flexible(true);
    csv_builder.has_headers(false);
    csv_builder.delimiter(b'\t');
    csv_builder.trim(csv::Trim::All);

    let mut csv_file = csv_builder.from_reader(file);

    for line in csv_file.records().filter_map(|line| line.ok()) {
        let region_name = line[0].to_owned();
        let modifications: Vec<isize> = line[1].split(",").map(|modification| modification.parse().unwrap()).collect();

        let region = AssembledRegion {
            modifications,
        };

        regions.insert(region_name, region);
    }

    regions
}

static LOOP_TYPES: &[(u32, &str)] = &[
    (VRNA_EXT_LOOP, "external"),
    (VRNA_HP_LOOP, "hairpin"),
    (VRNA_INT_LOOP, "internal"),
    (VRNA_MB_LOOP, "multibranch")
];

unsafe extern "C" fn accessibility_callback(v: *mut f64, v_size: i32, i: i32, _: i32, what: u32, data: *mut c_void) {
    if what & VRNA_PROBS_WINDOW_UP == 0 {
        return;
    }

    let what = what & !VRNA_PROBS_WINDOW_UP;

    unsafe {
        let data = data as *mut HashMap<isize, std::collections::HashMap<u32, std::vec::Vec<f64>>>;

        let data = data.as_mut().unwrap();

        let v = v.cast_slice(v_size.strict_cast_unsigned() as usize);

        let v = v.as_ref().unwrap();

        for (footprint, data) in data.iter_mut() {
            let start = i - *footprint as i32 + 1;

            if start <= 0 {
                continue;
            }

            let start_unsigned = start.strict_cast_unsigned() as usize;
            let footprint_unsigned = footprint.strict_cast_unsigned().strict_sub(1);

            data
                .get_mut(&what)
                .unwrap()[start_unsigned] = v[footprint_unsigned];
        }
    }
}

fn accessibility(sequence: &str, footprints: &[isize], window_size: isize, l: isize, m6a_sizes: Option<&[isize]>) ->HashMap<isize, HashMap<u32, Vec<f64>>> {
    let mut data: HashMap<isize, HashMap<u32, Vec<f64>>> = HashMap::new();

    let footprints: Vec<isize> = footprints.iter().filter(|fp| (**fp) as usize <= sequence.len() - 2).copied().collect();

    let max_footprint = footprints.iter().copied().max().unwrap();

    for footprint in footprints {
        let mut footprint_data = HashMap::new();

        for (loop_type, _) in LOOP_TYPES {
            let signed_sequence_length = sequence.len().strict_cast_signed();

            let signed_loop_type_data_length = signed_sequence_length - footprint + 2;

            if signed_loop_type_data_length < 0 {
                eprintln!("Sequence Length {signed_sequence_length}");
                eprintln!("Footprint {}", footprint);
                eprintln!("Signed loop type data length {}", signed_loop_type_data_length);
            }

            let unsigned_loop_type_data_length = signed_loop_type_data_length.strict_cast_unsigned();

            let loop_type_data = vec![0.0; unsigned_loop_type_data_length];

            footprint_data.insert(*loop_type, loop_type_data);
        }

        data.insert(footprint, footprint_data);
    }

    let mut md = vrna_md_t {
        temperature: Default::default(),
        betaScale: Default::default(),
        pf_smooth: Default::default(),
        dangles: Default::default(),
        special_hp: Default::default(),
        noLP: Default::default(),
        noGU: Default::default(),
        noGUclosure: Default::default(),
        logML: Default::default(),
        circ: Default::default(),
        circ_penalty: Default::default(),
        gquad: Default::default(),
        uniq_ML: Default::default(),
        energy_set: Default::default(),
        backtrack: Default::default(),
        backtrack_type: Default::default(),
        compute_bpp: Default::default(),
        nonstandards: [0;64],
        max_bp_span: Default::default(),
        min_loop_size: Default::default(),
        window_size: Default::default(),
        oldAliEn: Default::default(),
        ribo: Default::default(),
        cv_fact: Default::default(),
        nc_fact: Default::default(),
        sfact: Default::default(),
        rtype: Default::default(),
        alias: Default::default(),
        pair: Default::default(),
        pair_dist: Default::default(),
        salt: Default::default(),
        saltMLLower: Default::default(),
        saltMLUpper: Default::default(),
        saltDPXInit: Default::default(),
        saltDPXInitFact: Default::default(),
        helical_rise: Default::default(),
        backbone_length: Default::default(),
        circ_alpha0: Default::default(),
    };

    unsafe {
        vrna_md_set_default(&mut md as *mut vrna_md_t);
    }

    md.max_bp_span = l as i32;
    md.window_size = window_size as i32;

    let sequence_c_string = CString::new(sequence).unwrap();
    let sequence_c_str = sequence_c_string.as_c_str();

    unsafe {
        let fc = vrna_fold_compound(sequence_c_str.as_ptr(), &md as *const vrna_md_t, VRNA_OPTION_WINDOW);

        let modification_sites = if let Some(m6a_sites) = m6a_sizes {
            let modification_sites: Vec<usize> = m6a_sites.iter().map(|modification_site| modification_site.strict_cast_unsigned().strict_add(1)).collect();
            let mut modification_sites: Vec<u32> = modification_sites.into_iter().map(|modification_site| {
                if modification_site > u32::MAX as usize {
                    panic!("Modification site out of bounds {}", modification_site);
                }

                modification_site as u32
            }).collect();

            modification_sites.push(0);

            vrna_sc_mod_m6A(fc, modification_sites.as_ptr(), VRNA_SC_MOD_DEFAULT);

            Some(modification_sites)
        }
        else {
            None
        };

        let data_ptr = &mut data as *mut HashMap<isize, std::collections::HashMap<u32, std::vec::Vec<f64>>>;

        if max_footprint > i32::MAX as isize || max_footprint < i32::MIN as isize {
            panic!("Max footprint out of i32 bounds {max_footprint}");
        }

        vrna_probs_window(fc, max_footprint as i32, VRNA_PROBS_WINDOW_UP | VRNA_PROBS_WINDOW_UP_SPLIT, Some(accessibility_callback), data_ptr as *mut c_void);

        vrna_fold_compound_free(fc);

        drop(modification_sites)
    }

    data
}

static DONE_KEYS: &[&str] =&[];

static FILE_DICT: &[(&str, &str, &str)] = &[
    (
        "exons",
        "../../data/regions_fasta/region_exons.fna.gz",
        "../../data/regions_intersect_local_assembled/region_exons_intersect_local_assembled.gz"
    ),
    (
        "introns",
        "../../data/regions_fasta/region_introns.fna.gz",
        "../../data/regions_intersect_local_assembled/region_introns_intersect_local_assembled.gz"
    ),
    (
        "coding_exons",
        "../../data/regions_fasta/region_codingexons.fna.gz",
        "../../data/regions_intersect_local_assembled/region_codingexons_intersect_local_assembled.gz"
    ),
    (
        "coding_introns",
        "../../data/regions_fasta/region_codingintrons.fna.gz",
        "../../data/regions_intersect_local_assembled/region_codingintrons_intersect_local_assembled.gz"
    ),
    (
        "non_coding_exons",
        "../../data/regions_fasta/region_noncodingexons.fna.gz",
        "../../data/regions_intersect_local_assembled/region_noncodingexons_intersect_local_assembled.gz"
    ),
    (
        "non_coding_introns",
        "../../data/regions_fasta/region_noncodingintrons.fna.gz",
        "../../data/regions_intersect_local_assembled/region_noncodingintrons_intersect_local_assembled.gz"
    ),
    (
        "cds",
        "../../data/regions_fasta/region_cds.fna.gz",
        "../../data/regions_intersect_local_assembled/region_cds_intersect_local_assembled.gz"
    ),
    (
        "3utr",
        "../../data/regions_fasta/region_3utr.fna.gz",
        "../../data/regions_intersect_local_assembled/region_3utr_intersect_local_assembled.gz"
    ),
    (
        "5utr",
        "../../data/regions_fasta/region_5utr.fna.gz",
        "../../data/regions_intersect_local_assembled/region_5utr_intersect_local_assembled.gz"
    ),
    (
        "5utr_start",
        "../../data/regions_fasta/region_5utr_start.fna.gz",
        "../../data/regions_intersect_local_assembled/region_5utr_start_intersect_local_assembled.gz"
    )
];

static WINDOW_SIZES: &[isize] = &[150, 200, 350, 400];
static FOOTPRINTS: &[isize] = &[5, 10, 15, 20, 25, 30];
static L: isize = 100;

fn main()  {
    FILE_DICT.par_iter().for_each(|(key, fasta_path, modification_path)| {
        if DONE_KEYS.contains(key) {
            return;
        }

        println!("{key}");

        let regions = load_region_modifications(modification_path);

        let fasta = FastaReader::new(Path::new(fasta_path));

        std::fs::create_dir_all("../../data/accessibilities").unwrap();

        let output_path = format!("../../data/accessibilities/accessibilities_{key}.gz");

        let output_file = File::create(output_path).unwrap();

        let output_file = MultiGzDecoder::new(output_file);

        let mut csv_builder = csv::WriterBuilder::new();

        csv_builder.flexible(true);
        csv_builder.has_headers(false);
        csv_builder.delimiter(b'\t');

        let mut csv_writer = csv_builder.from_writer(output_file);

        for (i, [description, sequence]) in fasta.enumerate() {
            if i % 100 == 0 {
                println!("{key} {i}");
            }

            let name = description.strip_prefix(">").unwrap();
            let name = name.split(":").next().unwrap();

            if !regions.contains_key(name) {
                continue;
            }

            let sequence = sequence.to_uppercase().replace("T", "U");
            let sequence_length = sequence.len().strict_cast_signed();

            let modifications = &regions[name].modifications;
            let mut modifications = modifications.clone();
            modifications.sort();

            if modifications.is_empty() {
                continue;
            }

            for window_size in WINDOW_SIZES {
                let window_size_str = format!("{window_size}");

                let mut intervals: Vec<Interval> = Vec::with_capacity(modifications.len());

                for modification in &modifications {
                    intervals.push(get_interval_from_modification(*modification, *window_size, sequence_length));
                }

                let mut i = 0;

                while i < intervals.len() - 1 {
                    let interval_a = &intervals[i];
                    let interval_b = &intervals[i + 1];

                    if are_intervals_overlapping(interval_a, interval_b) {
                        let combined_interval = combine_intervals(interval_a, interval_b);

                        intervals[i] = combined_interval;
                        intervals.remove(i + 1);
                        continue;
                    }

                    i += 1;
                }

                for interval in intervals {
                    let start = interval.start;
                    let end = interval.end;
                    let interval_modifications = interval.modifications;

                    let start_str = format!("{start}");
                    let end_str = format!("{end}");

                    let interval_sequence = &sequence[start as usize..end as usize];

                    let adjusted_interval_modifications: Vec<isize> = interval_modifications.iter().map(|modification| *modification - start).collect();

                    let interval_modifications_str: Vec<String> = interval_modifications.iter().map(|modification| format!("{}", *modification)).collect();

                    let interval_modifications_str = interval_modifications_str.join(",");

                    let accessibilities_unmod = accessibility(interval_sequence, FOOTPRINTS, *window_size, L, None);
                    let accessibilities = accessibility(interval_sequence, FOOTPRINTS, *window_size, L, Some(&adjusted_interval_modifications));

                    for (footprint, fp_accessibilities_unmod) in accessibilities_unmod {
                        let footprint_str = format!("{footprint}");

                        for (feature, fp_f_accessibilities_unmod) in fp_accessibilities_unmod {
                            let fp_f_accessibilities_mod = &accessibilities[&footprint][&feature];

                            let fp_f_accessibilities_unmod_str: Vec<String> = fp_f_accessibilities_unmod.iter().map(|modification| format!("{}", *modification)).collect();
                            let fp_f_accessibilities_mod_str: Vec<String> = fp_f_accessibilities_mod.iter().map(|modification| format!("{}", *modification)).collect();

                            let fp_f_accessibilities_unmod_str = fp_f_accessibilities_unmod_str.join(",");
                            let fp_f_accessibilities_mod_str = fp_f_accessibilities_mod_str.join(",");

                            csv_writer.write_record([name, window_size_str.as_str(), start_str.as_str(), end_str.as_str(), footprint_str.as_str(), interval_modifications_str.as_str(), fp_f_accessibilities_unmod_str.as_str(), fp_f_accessibilities_mod_str.as_str()]).unwrap();
                        }
                    }
                }
            }
        }
    });

    println!("Done")
}

/*
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
