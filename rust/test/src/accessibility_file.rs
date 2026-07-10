use std::{io::{self, Read, Write}};

use rmp_serde::{from_slice, to_vec};
use serde::{Deserialize, Serialize};


#[derive(Debug, PartialEq, Deserialize, Serialize, Clone)]
pub struct AccessibilityComputationResult {
    pub region_name: String,
    pub window_size: usize,
    pub start: usize,
    pub end: usize,
    pub footprint: usize,
    pub feature: usize,
    pub modifications: Vec<usize>,
    pub accessibilities_unmod: Vec<f64>,
    pub accessibilities_mod: Vec<f64>
}

impl AccessibilityComputationResult {
    pub fn read_from<R: Read>(mut reader: R) -> Result<AccessibilityComputationResult, io::Error> {
        let mut size_buf = [0u8; 8];
        reader.read_exact(&mut size_buf)?;

        let size = usize::from_ne_bytes(size_buf);

        let mut buffer = vec![0u8; size];

        reader.read_exact(&mut buffer)?;

       let value =  from_slice::<AccessibilityComputationResult>(&buffer).unwrap();

       Ok(value)
    }

    pub fn write_to<W: Write>(&self, mut writer: W) -> Result<(), io::Error> {
        let buffer = to_vec(self).unwrap();

        let size = buffer.len();

        writer.write_all(&size.to_ne_bytes())?;

        writer.write_all(&buffer)?;

        Ok(())
    }
}
