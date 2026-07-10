use std::{collections::{HashMap, VecDeque}, fs::File, io::{Seek, SeekFrom}, os::unix::fs::MetadataExt};

use flate2::read::MultiGzDecoder;
use librna_sys::{VRNA_EXT_LOOP, VRNA_HP_LOOP, VRNA_INT_LOOP, VRNA_MB_LOOP};

use crate::accessibility_file::{AccessibilityComputationResult, AccessibilityComputationResultFile};

mod accessibility_file;
mod possibly_gzip_file;

static LOOP_TYPES: &[(u32, &str)] = &[
    (VRNA_EXT_LOOP, "external"),
    (VRNA_HP_LOOP, "hairpin"),
    (VRNA_INT_LOOP, "internal"),
    (VRNA_MB_LOOP, "multibranch")
];

fn loop_type_name(val: u32) -> &'static str {
    for i in 0..LOOP_TYPES.len() {
        if LOOP_TYPES[i].0 == val {
            return LOOP_TYPES[i].1;
        }
    }

    panic!("Unknown LOOP TYPE {}", val);
}

fn main()  {
    let input_path = "../../data/accessibilities/accessibilities_exons.gz";

    let input_file = File::open(input_path).unwrap();

    let input_file = AccessibilityComputationResultFile::new(input_file);

    let top_n = 10;

    let mut max_accessibilities: HashMap<usize, (f64, VecDeque<(f64, AccessibilityComputationResult)>)> = HashMap::new();
    let mut min_accessibilities: HashMap<usize, (f64, VecDeque<(f64, AccessibilityComputationResult)>)> = HashMap::new();

    for result in input_file {
        if result.end - result.start > 5000 {
            continue;
        }

        let diff: Vec<f64> = result.accessibilities_mod.iter()
            .zip(result.accessibilities_unmod.iter())
            .map(|(modified, unmod)| modified - unmod)
            .collect();

        let min = diff.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max = diff.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));

        if let Some(max_access) = max_accessibilities.get_mut(&result.feature) {
            if max > max_access.0 {
                max_access.0 = max;
                max_access.1.push_front((max, result.clone()));

                if max_access.1.len() > top_n {
                    max_access.1.pop_back();
                }
            }
            else {
                if max_access.1.len() < top_n {
                    for i in 0..max_access.1.len() {
                        if max > max_access.1[i].0 {
                            max_access.1.insert(i, (max, result.clone()));
                        }
                    }
                }
            }
        }
        else {
            let mut vec = VecDeque::new();

            vec.push_front((max, result.clone()));

            max_accessibilities.insert(result.feature, (max, vec));
        }

        if let Some(min_access) = min_accessibilities.get_mut(&result.feature) {
            if min < min_access.0 {
                min_access.0 = min;
                min_access.1.push_front((min, result.clone()));

                if min_access.1.len() > top_n {
                    min_access.1.pop_back();
                }
            }
            else {
                if min_access.1.len() < top_n {
                    for i in 0..min_access.1.len() {
                        if min < min_access.1[i].0 {
                            min_access.1.insert(i, (min, result.clone()));
                        }
                    }
                }
            }
        }
        else {
            let mut vec = VecDeque::new();

            vec.push_front((min, result.clone()));

            min_accessibilities.insert(result.feature, (min, vec));
        }
    }

    for (loop_type, max_access) in max_accessibilities {
        let translated_loop_type_name = loop_type_name(loop_type as u32);

        let path = format!("../../data/access_max_{}.csv",translated_loop_type_name);

        let output_file = File::create(path).unwrap();

        let mut csv_builder = csv::WriterBuilder::new();

        csv_builder.flexible(true);
        csv_builder.has_headers(false);
        csv_builder.delimiter(b'\t');

        let mut csv_file = csv_builder.from_writer(output_file);

        for (max_value, result) in max_access.1 {
            let modifications: Vec<String> = result.modifications.iter().map(|modif| format!("{}", modif)).collect();
            csv_file.write_record([&format!("{}", max_value), &result.region_name, &format!("{}", result.footprint), &format!("{}", result.start), &format!("{}", result.end), &modifications.join(",")]).unwrap();
        }
    }


    for (loop_type, min_access) in min_accessibilities {
        let translated_loop_type_name = loop_type_name(loop_type as u32);

        let path = format!("../../data/access_min_{}.csv",translated_loop_type_name);

        let output_file = File::create(path).unwrap();

        let mut csv_builder = csv::WriterBuilder::new();

        csv_builder.flexible(true);
        csv_builder.has_headers(false);
        csv_builder.delimiter(b'\t');

        let mut csv_file = csv_builder.from_writer(output_file);

        for (min_value, result) in min_access.1 {
            let modifications: Vec<String> = result.modifications.iter().map(|modif| format!("{}", modif)).collect();
            csv_file.write_record([&format!("{}", min_value), &result.region_name, &format!("{}", result.footprint), &format!("{}", result.start), &format!("{}", result.end), &modifications.join(",")]).unwrap();
        }
    }

    println!("Done")
}
