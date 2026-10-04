# Synthetic fixtures for the evidence page

**These are not student data.** All 30 "students", scores, build records and survey answers were generated at random (seed 1) to test the statistics on `evidence.html`.

The reference values in `../check-evidence.cjs` were computed independently with SciPy 1.17 (`scipy.stats.ttest_rel`, `pearsonr`, `t.interval`) and NumPy, for example:
- paired t-test t(27) = 4.84, mean change 95% CI [0.093, 0.229], d_z = 0.915, Hedges' g_av = 0.794;
- within-course t(29) = 3.57, d_z = 0.652;
- r(A3–A9, final) = 0.803 [0.623, 0.902];
- Cronbach's α for the Engagement scale = 0.903.
