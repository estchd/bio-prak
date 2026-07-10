use std::{fs::File, io::Read};

use flate2::read::MultiGzDecoder;

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
