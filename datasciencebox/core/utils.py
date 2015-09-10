import os
import sys
import time
import fileinput

from datasciencebox.core.exceptions import DSBException


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def retry(retries=10, wait=5, catch=None):
    """
    Decorator to retry on exceptions raised
    """
    catch = catch or (Exception,)

    def real_retry(function):

        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    ret = function(*args, **kwargs)
                    return ret
                except catch:
                    time.sleep(wait)
                except Exception as e:
                    raise e
                else:
                    raise DSBException('Retries limit exceded.')

        return wrapper

    return real_retry


def replace_all(file, searchExp, replaceExp):
    """
    Replace all the ocurrences (in a file) of a string with another value.
    """
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp, replaceExp)
        sys.stdout.write(line)
