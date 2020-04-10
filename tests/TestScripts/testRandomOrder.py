#!/usr/bin/env python3

import subprocess
import sys
import xml.etree.ElementTree as ET

def list_tests(self_test_exe, tags, rng_seed):
    cmd = [self_test_exe, '--reporter', 'xml', '--list-tests', '--order', 'rand',
            '--rng-seed', str(rng_seed)]
    tags_arg = ','.join('[{}]'.format(t) for t in tags)
    if tags_arg:
        cmd.append(tags_arg + '~[.]')
    process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        raise RuntimeError("Unexpected error output:\n" + process.stderr)

    root = ET.fromstring(stdout)
    result = [elem.text for elem in root.findall('./TestCase/Name')]

    if len(result) < 2:
        raise RuntimeError("Unexpectedly few tests listed (got {})".format(
            len(result)))
    return result

def check_is_sublist_of(shorter, longer):
    assert len(shorter) < len(longer)
    assert len(set(longer)) == len(longer)

    indexes_in_longer = {s: i for i, s in enumerate(longer)}
    for s1, s2 in zip(shorter, shorter[1:]):
        assert indexes_in_longer[s1] < indexes_in_longer[s2], (
                '{} comes before {} in longer list.\n'
                'Longer: {}\nShorter: {}'.format(s2, s1, longer, shorter))

def main():
    self_test_exe, = sys.argv[1:]

    list_one_tag = list_tests(self_test_exe, ['generators'], 1)
    list_two_tags = list_tests(self_test_exe, ['generators', 'matchers'], 1)
    list_all = list_tests(self_test_exe, [], 1)

    # First, verify that restricting to a subset yields the same order
    check_is_sublist_of(list_two_tags, list_all)
    check_is_sublist_of(list_one_tag, list_two_tags)

    # Second, verify that different seeds yield different orders
    num_seeds = 100
    seeds = range(1, num_seeds + 1) # Avoid zero since that's special
    lists = {tuple(list_tests(self_test_exe, [], seed)) for seed in seeds}
    assert len(lists) == num_seeds, (
            'Got {} distict lists from {} seeds'.format(len(lists), num_seeds))

if __name__ == '__main__':
    sys.exit(main())
