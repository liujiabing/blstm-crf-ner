#!/usr/bin/env python

import glob
import errno
import subprocess

# Overall results
acc = 0.0
pre = 0.0
rec = 0.0
f1  = 0.0
entity_res = dict()

model_output_files = glob.glob('./conlleval*.tmp')
for i, model_output in enumerate(model_output_files):
    try:
        # Run conlleval for each output file
        p = subprocess.Popen('python2 conlleval.py {} > model_metrics{}.tmp'.format(model_output, str(i+1)),
                             shell=True, stdout=subprocess.PIPE, universal_newlines=True,
                             stderr=subprocess.STDOUT)
        result_code = p.wait()
        if result_code == 0:
            with open('model_metrics{}.tmp'.format(str(i+1)), 'r') as f:
                for j, line in enumerate(f):
                    # SKip first line
                    if j == 0:
                        continue
                    tokens = line.strip().split()
                    # Second line consists of overall results
                    if j == 1:
                        acc += float(str(tokens[1]).replace("%;", ""))
                        pre += float(str(tokens[3]).replace("%;", ""))
                        rec += float(str(tokens[5]).replace("%;", ""))
                        f1  += float(str(tokens[7]).replace("%;", ""))
                    else:
                        entity_type = tokens[0]
                        if entity_type not in entity_res:
                            entity_res[entity_type] = {"pre": 0.0, "rec": 0.0, "f1": 0.0, "count": 0}
                        entity_res[entity_type]["pre"] += float(str(tokens[2]).replace("%;", ""))
                        entity_res[entity_type]["rec"] += float(str(tokens[4]).replace("%;", ""))
                        entity_res[entity_type]["f1"] += float(str(tokens[6]).replace("%;", ""))
                        entity_res[entity_type]["count"] += 1
        else:
            p_out = p.stdout.read().decode('unicode_escape')
            print("Error #{} - {}".format(str(i+1), p_out))
    except IOError as exc:  # Not sure what error this is
        if exc.errno != errno.EISDIR:
            raise

print("Overall:")
print("Accuracy: {:.5f}".format(acc / (i+1)))
print("Precision: {:.5f}".format(pre / (i+1)))
print("Recall: {:.5f}".format(rec / (i+1)))
print("F1: {:.5f}".format(f1 / (i+1)))
print("-----------------------------")
print("Entity types:")
for entity_type, metrics in entity_res.items():
    c = metrics["count"]
    print("{} Precision: {:.5f}, Recall: {:.5f}, F1: {:.5f}".format(entity_type,
                                                                     metrics["pre"] / (i+1),
                                                                     metrics["rec"] / (i + 1),
                                                                     metrics["f1"] / (i+1)))
