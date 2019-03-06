# -*- coding: utf-8 -*-

class MissingMetadata(Exception):
    """ Missing metadata
    The key 'meta_url' is missing from apps.json or
    the value of 'meta_url' is wrong/missing.
    """
    pass


class WrongMetadata(Exception):
    """ Wrong metadata
    The provided metadata.json file cannot be loaded by Python's built-in json.loads method.
    The metadata.json file may not be a correct JSON file.
    """
    pass


class MissingGit(Exception):
    """ Missing git URL
    The key 'git_url' is missing from apps.json or
    the value of 'git_url' is wrong/missing.
    """
    pass


class MissingCategories(Exception):
    """ Missing categories
    The key 'categories' is missing from apps.json or
    the value of 'categories' is wrong/missing.
    """
    pass


class WrongCategory(Exception):
    """ Wrong category
    The specified category does not exist in categories.json.
    """
    pass
