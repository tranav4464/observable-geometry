# Two-minute explanation

EEG records electrical patterns at the scalp. Researchers use those measurements and a head model to estimate where activity might have come from. But two distant brain locations can produce very similar predicted scalp patterns. A detailed-looking map can therefore hide uncertainty about location.

I built Observable Geometry to make that ambiguity easier to inspect. You give it a forward model, a matching noise covariance, source coordinates and information about how the model was constructed. It compares the predicted patterns, accounts for noise and lists distant alternatives for each source location.

The output is concrete: a ranked CSV, numerical scores, a summary, and a record of the inputs and code used. A researcher can inspect which distant alternatives their model struggles to separate before making a spatially specific claim.

I started by reproducing and reverse-engineering a GBFs workflow. I then built a separate diagnostic with input validation, numerical tests and checks that prevent it from accidentally opening EEG sample arrays. On one verified participant model with 8,196 candidate sources, the tool produces 40,980 ranked rows. A fresh installed package reproduced those outputs exactly, and a separately written calculation reproduced every ranking.

The mathematics behind the similarity score already exists. My contribution is the software workflow and the inspectable evidence, and I am keeping that distinction clear. This does not prove that we recovered real neural sources, and we have not yet shown better decisions than established source-resolution tools. The next version needs an eligible measured-data test and external researcher feedback on whether this report changes a useful decision.
