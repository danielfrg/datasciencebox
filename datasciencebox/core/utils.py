import time

from datasciencebox.core.exceptions import DSBException


def retry(retries=10, wait=5, catch=None):
    catch = catch or (Exception, )

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
