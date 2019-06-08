import os
import collections
import argparse
import json
from git import Repo

from analyse_file_names import get_top_verbs_in_path, get_top_functions_names_in_path, TOP_COMMON
from nltk import pos_tag

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

languages = [
    '.py'
]

searchers = [
    'names',
    'verbs'
]

reports = [
    'json',
    'csv',
    'console'
]

parser = argparse.ArgumentParser()
parser.add_argument('url')
parser.add_argument("language")
parser.add_argument("searcher")
parser.add_argument("report_type")
args = parser.parse_args()
# print(args)


def clone_repo(git_url):
    try:
        git_dir = git_url.rsplit('/', 1)[1].split('.')[0]
        Repo.clone_from(git_url, f"{BASE_DIR}/{git_dir}")
    except:
        raise ValueError('Repo clone error.')
    return git_dir


if __name__ == "__main__":

    words = []

    git_dir = clone_repo(args.url)

    if not args.url.endswith('.git'):
        print('This is not a git repository.')
        exit(1)

    if args.language not in languages:
        print('This language is not supported.')
        exit(1)

    if args.searcher not in searchers:
        print('Incorrect search terms.')
        exit(1)

    if args.report_type not in reports:
        print('Incorrect type.')
        exit(1)

    if args.searcher == 'verbs':
        words = get_top_verbs_in_path(git_dir, args.language)
    elif args.searcher == 'names':
        words = get_top_functions_names_in_path(git_dir, args.language)

    print('total %s words, %s unique' % (len(words), len(set(words))))

    result_json = dict()

    for word, occurence in collections.Counter(words).most_common(TOP_COMMON):

        if args.report_type == 'console':
            print(word,  occurence)

        elif args.report_type == 'json':
            result_json.update({str(word)[1:-1]: occurence})

        elif args.report_type == 'csv':
            string = str(word)[1:-1] + ', ' + str(occurence)

            with open('result.csv', 'a') as file:
                file.write(string)


    if args.report_type == 'json':
        with open('result.json', 'w') as json_file:
            json.dump(result_json, json_file)
