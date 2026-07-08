use std::ffi::CStr;

use librna_sys::{vrna_fold_compound_t, vrna_fold_compound_free};

use crate::model_details::ModelDetails;

pub struct FoldCompound {
    vrna_fold_compound: *mut vrna_fold_compound_t
}

impl FoldCompound {
    pub fn new_cstr(sequence: &CStr, model_details: Option<ModelDetails>, ) -> Self {
        todo!()
    }

    pub fn new_str(sequence: &str,  model_details: Option<ModelDetails>) -> Self {
        todo!()
    }
}

impl Drop for FoldCompound {
    fn drop(&mut self) {
        unsafe {
            vrna_fold_compound_free(self.vrna_fold_compound);
        }
    }
}
