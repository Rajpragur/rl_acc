# TGSIM I-294 L2 dataset: inspected, not used as a score benchmark

`I294_L2_final.csv` is the public U.S. DOT / FHWA TGSIM I-294 Level 2 trajectory file. The catalog describes two L2 test vehicles through lane-change maneuvers and then a string with ACC enabled, with vehicle position, speed and acceleration at 0.1 s intervals. The downloaded CSV is about 12 MB and contains 137,928 rows.

The dataset is useful for a future real-trajectory replay, but it does not give a clean labeled external cut-in into an ACC vehicle that we can fairly score against our controller. Its ACC test vehicles are themselves doing the documented automated lane changes before joining the string, and engagement timing must be established before making a controller comparison. We therefore keep it as a reviewed candidate and use the clearer JRC OpenACC car-following record only for a descriptive headway reference.

Source: [U.S. DOT TGSIM I-294 L2 Trajectories](https://catalog.data.gov/dataset/third-generation-simulation-data-tgsim-i-294-l2-trajectories). The catalog lists public access and the U.S. public-domain license label.
