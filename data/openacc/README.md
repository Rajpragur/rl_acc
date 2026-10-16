# OpenACC reference trace

This folder contains one short sample from the European Commission Joint Research Centre's Open ACC Database. The trace is used only to give the presentation a real-road commercial ACC reference.

- Campaign: Vicolungo, 26 February 2019
- Recording: `JRC-VC_260219_part2.csv`
- Lead: Mitsubishi SpaceStar, Human driver
- First follower: Ford S-Max, ACC active, minimum distance setting
- The campaign notes report original GNSS sampling at roughly 3–5 Hz, with spline interpolation to 10 Hz.
- The EU's copyright notice states CC BY 4.0; the source must be credited and changes indicated.

Source: European Commission Joint Research Centre, [Open ACC Database](https://data.jrc.ec.europa.eu/dataset/9702c950-c80f-4d2f-982f-44d06ea0009f), DOI `10.2905/JRC.KMH3D00`; dataset paper: Makridis et al. (2021), DOI `10.1016/j.trc.2021.103047`.

The CSV is an official source subset. `src/analyze_openacc.py` produces a descriptive summary at `outputs/openacc_reference.json`. Headway statistics are computed as bumper-to-bumper inter-vehicle spacing divided by follower speed. This is a contextual reference from one 2019 minimum-distance run, not a direct cut-in controller benchmark and not a description of every modern production system.
