# This script converts the original GermEval 2014 NER Shared Task data
# files (https://sites.google.com/site/germeval2014ner/data) to the unified
# input format of the model (each line containing space-separated lists
# of tokens and labels of a single sentence, separated by a tab). Only
# outer span labels (third column in the original files) are taken into
# account and used for deriving pre-processed labels. It is assumed that
# the three original files - "NER-de-train.tsv", "NER-de-dev.tsv", and
# "NER-de-test.tsv" are copied into --source-folder (-s). By default,
# the tags are converted to IOBES tagging scheme (this may be switched
# off by setting --iobes (-i) to False, to get IOB2 tags).The pre-processing
# results are written into --target-folder (-t), from where a model can be
# trained directly using train.py.


import os
import argparse

import common


def convert():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source-folder", type=str, default="../data/sources/germeval")
    parser.add_argument("-t", "--target-folder", type=str, default="../data/ready/nerc/germeval")
    parser.add_argument("-i", "--iobes", type=bool, default=True)
    args = parser.parse_args()

    print("Source folder: {}".format(args.source_folder))
    print("Target folder: {}".format(args.target_folder))
    print("Convert to IOBES: {}".format(args.iobes))
    print()

    sentence_pairs_per_file = {}

    for file in os.listdir(args.source_folder):
        sentence_pairs_per_file[file] = []
        file_path = os.path.join(args.source_folder, file)
        file_lines = [l[:-1] for l in open(file_path, encoding="utf-8").readlines()]

        print("processing data from {}".format(file_path))

        running_pairs = []
        for line in file_lines + [""]:
            if line == "" or line.startswith("#\t"):
                if len(running_pairs) > 0:
                    sentence_pairs_per_file[file].append(
                        common.convert_to_iobes_tags(running_pairs)
                        if args.iobes else running_pairs
                    )
                    running_pairs = []
                continue
            pair = line.split("\t")[1:3]
            running_pairs.append(pair)

    if not os.path.exists(args.target_folder):
        os.makedirs(args.target_folder)

    label_count_pairs = common.get_label_count_pairs(sentence_pairs_per_file)
    common.report_statistics(sentence_pairs_per_file, label_count_pairs)

    for target, source in [
        ["train", "NER-de-train.tsv"],
        ["val", "NER-de-dev.tsv"],
        ["test", "NER-de-test.tsv"]
    ]:
        sentences_written, tokens_written = 0, 0
        out_path = os.path.join(args.target_folder, target + ".txt")

        with open(out_path, "w+", encoding="utf-8") as out:
            for sentence in sentence_pairs_per_file[source]:
                out.write("{}\t{}\n".format(
                    " ".join([p[0] for p in sentence]),
                    " ".join([p[1] for p in sentence]),
                ))
                tokens_written += len(sentence)
            sentences_written += len(sentence_pairs_per_file[source])

        print("data from {} ({:,} sentences, {:,} tokens) written to {}".format(
            source, sentences_written, tokens_written, out_path
        ))

    label_path = os.path.join(args.target_folder, "labels.txt")
    with open(label_path, "w+", encoding="utf-8") as out:
        for lb in label_count_pairs:
            out.write("{}\n".format(lb[0]))

    print("{} labels written to {}".format(
        len(label_count_pairs), label_path
    ))


if __name__ == "__main__":
    convert()
