pingback_service
Differences Between Mini Program/App Rules and PC/WAP Rules
The data fields used in both versions differ, but this does not affect the overall result comparison.
In Mini Program/App, the ev field's d code is always a number, allowing continuity checks and more accurate sorting. In PC/WAP, d may be a string, preventing continuity validation and following string-based sorting rules.
In Mini Program/App, a test session without PV (Page View) and EV (Exposure View) is considered a severe exception, and no summary results will be generated. In PC/WAP, only the absence of PV is treated as a severe exception.
In Mini Program/App, the creation of basic rules is not allowed if spmcnt is empty, whereas in PC/WAP, empty spmcnt values are permitted.
In Mini Program/App, the recommendation strategy is fixed, and specific value comparisons are performed. In PC/WAP, if scm starts with "1," the presence of scm is compared rather than the exact values; otherwise, values must match exactly.
