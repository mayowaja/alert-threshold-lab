# Alert Threshold Lab

How do you choose which model scores should trigger a security alert? This experiment assigns a cost to false alarms and missed risks, selects a threshold on validation data, then measures its performance on a separate test set. It runs offline with Python 3.11+ and the standard library.

## Reproduce the experiment

```sh
python thresholds.py examples/scores.csv --miss-cost 1
python thresholds.py examples/scores.csv --miss-cost 4
python -m unittest discover -s tests -v
```

| Cost of one miss | Selected threshold | False alarms on test | Misses on test |
| --- | ---: | ---: | ---: |
| 1 | 0.83 | 0 | 2 |
| 4 | 0.59 | 2 | 1 |

In the supplied example, accepting two extra false alarms catches one additional risk among eight held-out records. This illustrates the decision an engineer faces when triage capacity is limited.

## Method

The input columns are `id,split,score,label`. Use a unique ID per observation, a split of `validation` or `test`, a finite score between zero and one, and a verified binary label (1 means risk). Each split must contain both classes.

A score at or above the threshold produces an alert. The program checks every distinct validation score and the option of raising no alerts. It minimises false alarms plus missed risks multiplied by the chosen miss cost. Equal-cost policies are resolved in favour of the higher threshold. Test labels are used only in the final evaluation. TP, FP, TN and FN denote true positives, false positives, true negatives and false negatives.

## Scope

The CSV contains 16 invented examples. No trained model or dissertation dataset is bundled. These scores illustrate threshold selection and do not establish predictive performance. To evaluate your own model, export its out-of-sample scores and keep related resources together when forming splits. The direct search favours readability and is intended for small datasets.
