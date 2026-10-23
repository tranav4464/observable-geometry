# B4 channel-contract reconciliation

**Date:** 24 October 2026

The exploratory output `outputs/track_b/20261023T192200Z_b4_dev_protocol_feasibility/b4_site_associations.csv` must not be used as matched-method evidence. Its manifest shows that the GBF score and MNE resolution inputs came from sealed 236-channel artifacts, while the empirical report describes a 224-channel intersection. The same rows therefore join outputs produced under different sensor contracts.

The invalid CSV and manifest are preserved unchanged as failure evidence. The initial failed attempt is also preserved; it failed before output because an audit script expected the wrong capitalization for two report keys and did not access recording samples.

A later fresh run, `outputs/20261023T192900Z_b4_matched_224_reproduction`, executed the existing empirical script with its own common 224-channel contract. Its pair table matches the sealed Track A pair table byte-for-byte (both SHA-256 `d3808dfb22318df1fc8fab6a06c4e20c8a059622dca93465029da2619396f50b`). It reports 224 common channels, six sites, 15 dependent site-pairs, a −2 to +2 ms observation window, Pearson `r = 0.34516194307310066`, and Spearman `rho = 0.3428571428571428`.

This resolves reproducibility of the existing 224-channel Track A calculation. It does **not** make the 236-channel B2/B3 artifacts matched to the empirical data, does not compare B2 similarity directly with an MNE PSF/CTF under the 224-channel contract, and does not validate endogenous neural source recovery. The rerun remains an exposed, one-participant, pulse-artifact development analysis.
