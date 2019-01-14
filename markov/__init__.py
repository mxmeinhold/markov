"""
Module markov.

Provides functionality for processing a list of sentences into a markov chain
and generating output based on that chain.
"""

import random
import string
import os
import requests

if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    import config
else:
    import env_config as config


# Initialisation
_START = 'START'
_END = 'END'
_GRAPH = {_START : []}
_TRANSLATE_TABLE = str.maketrans({key : None for key in string.punctuation})


def reset():
    """
    Resets the internal markov chain
    """
    _GRAPH.clear()
    _GRAPH[_START] = []

def source_api(speaker=None, submitter=None):
    """
    Pulls quotes from the quotefault api
    :param speaker: optional: sets a speaker's username to filter by
    :param submitter: optional: sets a submitter's username to filter by
    :return: a list of quote strings matching the criteria
    """
    query_args = ''
    if speaker is not None:
        query_args += 'speaker=' + speaker
    if submitter is not None:
        if query_args != '':
            query_args += '&'
        query_args += 'submitter=' + submitter
    if query_args != '':
        query_args = '?' + query_args
    quotes = requests.get(config.API_URL + config.API_KEY + '/all' + query_args).json()
    return [quote['quote'] for quote in quotes]


def parse(source):
    """
    Loads a list of quotes into the internal markov chain
    """
    for quote in source:
        _parse_one(quote.lower())


def _parse_one(quote):
    """
    Parses a single quote into the markov chain
    """
    # Remove punctuation and whitespace to make matching more likely
    words = list(word.translate(_TRANSLATE_TABLE).strip() for word in quote.split(' '))

    # Link every word to following words, and START -> beginning, end -> END
    _GRAPH[_START].append(words[0])
    for index, word in enumerate(words[:-1]):
        if word not in _GRAPH:
            _GRAPH[word] = []
        _GRAPH[word].append(words[index + 1])
    if words[-1] not in _GRAPH:
        _GRAPH[words[-1]] = []
    _GRAPH[words[-1]].append(_END)


def generate():
    """
    Generates a quote based on the internal markov chain.
    :raises: ValueError: if parsing has not occured and the internal chain is invalid
    """
    # If not parsed, fail.
    if not _GRAPH[_START]:
        raise ValueError("Please initilise the internal chain using parse()")

    # Walk through randomly selecting a following word until you hit an end
    out = []
    word = _START
    word = random.choice(_GRAPH[word])
    while word is not _END:
        out.append(word)
        word = random.choice(_GRAPH[word])
    return ' '.join(out)


def generate_list(number):
    """
    Returns a list of (length = number) quotes
    """
    out = []
    for _ in range(number):
        out.append(generate())
    return out
