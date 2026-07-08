use std::{ffi::CStr, sync::{Mutex, MutexGuard}};

use librna_sys::{vrna_md_copy, vrna_md_option_string, vrna_md_set_default, vrna_md_t, vrna_md_update};

static OPTIONS_STRING: Mutex<Option<&'static CStr>> = Mutex::new(None);

pub struct ModelDetails {
    pub vrna_md: vrna_md_t
}

impl ModelDetails {
    pub fn new() -> Self {
        unsafe {
            let mut uninitialized = Self::new_uninitialized();

            uninitialized.set_defaults();

            uninitialized
        }
    }

    /// # Safety
    /// The returned ModelDetails need to be initialized with set_defaults or by using copy_to with an initialized ModelDetails
    pub unsafe fn new_uninitialized() -> Self {
        let vrna_md = vrna_md_t {
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
            nonstandards: [0; 64],
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

        Self {
            vrna_md,
        }
    }

    pub fn update(&mut self) {
        unsafe {
            vrna_md_update(&mut self.vrna_md as *mut vrna_md_t);
        }
    }

    pub fn set_defaults(&mut self) {
        unsafe {
            vrna_md_set_default(&mut self.vrna_md as *mut vrna_md_t);
        }
    }

    pub fn copy_to(&self, other: &mut Self) {
            unsafe {
                vrna_md_copy(&mut other.vrna_md as *mut vrna_md_t, &self.vrna_md as *const vrna_md_t);
            }
    }

    pub fn option_string(&mut self) -> MutexGuard<'_, Option<&'static CStr>> {
        let mut guard = OPTIONS_STRING.lock().unwrap();

        unsafe {
            let cstr_ptr = vrna_md_option_string(&mut self.vrna_md as *mut vrna_md_t);

            let cstr: &'static CStr = CStr::from_ptr::<'static>(cstr_ptr);

            *guard = Some(cstr);
        }

        guard
    }


}

impl Clone for ModelDetails {
    fn clone(&self) -> Self {
        unsafe {
            let mut new = Self::new_uninitialized();

            self.copy_to(&mut new);

            new
        }
    }
}

impl Default for ModelDetails {
    fn default() -> Self {
        Self::new()
    }
}
