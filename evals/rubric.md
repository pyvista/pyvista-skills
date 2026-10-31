# Response quality rubric for PyVista skills

<!-- judge:begin -->
<!-- Everything between the judge:begin and judge:end markers is sent verbatim to
     the grader by scripts/judge.py. Keep condition names (and anything else that
     could identify which system produced a response) outside this block. -->

Judge responses blind: label them `A`, `B`, or `C` without exposing the condition name. Score each dimension from 1 (fails) to 5 (excellent).

| Dimension     | Weight | What to measure                                                                                                                                     |
| ------------- | -----: | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness   |    35% | PyVista/VTK technical accuracy: dataset types, filter contracts, I/O behavior; required details preserved                                           |
| Verification  |    25% | Runs the code and judges output from observed results — screenshot pixels, `bounds`, `n_points`, element counts — never from "the code looks right" |
| Actionability |    20% | The next action or answer is easy to find and execute                                                                                               |
| Safety        |    10% | Risk, confirmation, ambiguity, and render-environment choices (off-screen vs interactive) handled correctly                                         |
| Concision     |    10% | No filler or tangents; brevity does not remove needed substance                                                                                     |

Mark `blocker: true` for a dangerous instruction, a materially wrong PyVista or VTK claim, a failure to follow an explicit output contract, code that would fail at run time (wrong `add_mesh` arguments, `show()` before more actors), or a render presented as verified without observed output.
<!-- judge:end -->

Release the candidate only when:

1. It has no blocking findings.
2. Correctness and safety are each within 0.1 points of baseline or better.
3. Its weighted score is higher than baseline.
4. Any public competitor claim uses the same cases, models, trials, and rubric.
