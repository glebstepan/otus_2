import ast
import os
import collections

from nltk import pos_tag

TOP_COMMON = 200


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'


def get_trees(_path, language, with_filenames=False, with_file_content=False):
    file_names = []
    trees = []
    for dirname, dirs, files in os.walk(_path, topdown=True):
        for file in files:
            if file.endswith(language):
                file_names.append(os.path.join(dirname, file))

    print('total %s files' % len(file_names))
    for file_name in file_names:
        with open(file_name, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()

        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None

        if with_filenames:
            if with_file_content:
                trees.append((file_name, main_file_content, tree))
            else:
                trees.append((file_name, tree))
        else:
            trees.append(tree)

    # print('trees generated')
    return trees


def get_all_names(tree):
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_verbs_from_function_name(function_name):
    return [word for word in function_name.split('_') if is_verb(word)]


def split_snake_case_name_to_words(name):
    return [n for n in name.split('_') if n]


def get_all_words_in_path(path, language):
    trees = [t for t in get_trees(path, language) if t]
    function_names = [f for f in flat([get_all_names(tree) for tree in trees]) \
                      if not (f.startswith('__') and f.endswith('__'))]
    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names])


def get_top_verbs_in_path(path, language):
    trees = [t for t in get_trees(path, language) if t]
    extracted_functions = [f for f in flat([[node.name.lower() \
                              for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)] \
                             for tree in trees]) if not (f.startswith('__') and f.endswith('__'))]

    # print('functions extracted')
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in extracted_functions])
    return collections.Counter(verbs).most_common(TOP_COMMON)


def get_top_functions_names_in_path(path, language):
    trees = get_trees(path, language)
    functions_names = [f for f in flat([[node.name.lower() for node in ast.walk(tree) \
                                         if isinstance(node, ast.FunctionDef)] for tree in trees]) \
                       if not (f.startswith('__') and f.endswith('__'))]
    return collections.Counter(functions_names).most_common(TOP_COMMON)
