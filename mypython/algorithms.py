import RNA

# A dictionary with all types of loops distinguished in the
# unpaired probability computations of the ViennaRNA Package
looptypes = { RNA.EXT_LOOP : "external",
              RNA.HP_LOOP : "hairpin",
              RNA.INT_LOOP : "internal",
              RNA.MB_LOOP : "multibranch"
}

def accessibility(sequence, footprints = 30, windowsize = 200, L = 150, m6A_sites = None):
    """
    Compute unpaired probabilities for a set of (or single) footprint(s)
    using a sliding-window local RNA secondary structure prediction.

    The function returns a dictionary of unpaired probabilities for
    each footprint. Here, the keys are the individual footprint sizes
    as specified in the input argument 'footprints'. Each of the
    corresponding values is a dictionary again, where the keys are the
    individual loop types the footprint may reside in and the values are
    lists of probabilities where the i-th value is the probability of
    a footprint starting at position i.
    """

    def up_callback(v, v_size, i, maxsize, what, data):
        """
        Store accessibility data callback function
        """
        # only process unpaired probabilities
        if what & RNA.PROBS_WINDOW_UP:
            # mask variable 'what' such that it assumes
            # one of the vaues in 'looptypes'
            what = what & ~RNA.PROBS_WINDOW_UP
            #if i % 100 == 0:
            #    print(i)
            for fp in data.keys():
                # we store data for footprints starting
                # at position i, but 'probs_window()' yields
                # data ending at position i. So we need to
                # compute actual start position of the footprint
                start = i - fp + 1
                if start > 0:
                    dat = data[fp][what][start] = v[fp]

    # store footprints as list of footprint sizes
    fps = footprints if type(footprints) is list else [ footprints ]
    fps = [ int(fp) for fp in fps ]

    # create data structure (dict of dicts of lists) where we will store
    # the computed accessibilities. After filling the data structure, we
    # can obtain the resulting unpaired probabilities for each footprint
    # of size 'fp', starting at position 'i' and residing in loop type
    # 'lt' as:
    # p = data[fp][lt][i]
    data = { k : { lt : [ 0 for i in range(len(sequence) - k + 2) ] for lt in looptypes } for k in fps }

    # create model details and set windowsize and maximum base pair span
    md = RNA.md()
    md.max_bp_span = L
    md.window_size = windowsize

    # create fold_compound for sliding-window computations
    fc = RNA.fold_compound(sequence.upper(), md, RNA.OPTION_WINDOW)
    
    if m6A_sites:
        fc.sc_mod_m6A(m6A_sites)

    # compute sliding-window probabilities
    fc.probs_window(max(fps),
                    RNA.PROBS_WINDOW_UP | RNA.PROBS_WINDOW_UP_SPLIT,
                    up_callback,
                    data)

    return data