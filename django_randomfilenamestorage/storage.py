from errno import EEXIST
import os
import posixpath
import random
import string
from warnings import warn

from django.conf import settings
from django.core.files.storage import Storage, FileSystemStorage


CHARACTERS = string.lowercase + string.digits
DEFAULT_LENGTH = 16


def random_string(length):
    return ''.join(random.choice(CHARACTERS) for i in xrange(length))


def RandomFilenameMetaStorage(storage_class, length=None, uniquify_names=True):
    class RandomFilenameStorage(storage_class):
        def __init__(self, *args, **kwargs):
            self.randomfilename_length = kwargs.pop('randomfilename_length',
                                                    length)
            if self.randomfilename_length is None:
                self.randomfilename_length = getattr(settings,
                                                     'RANDOM_FILENAME_LENGTH',
                                                     DEFAULT_LENGTH)
            # Do not uniquify filenames by default.
            self.randomfilename_uniquify_names = kwargs.pop('uniquify_names',
                                                            uniquify_names)
            # But still try to tell storage_class not to uniquify filenames.
            # This class will be the one that uniquifies.
            try:
                new_kwargs = dict(kwargs, uniquify_names=False)
                super(RandomFilenameStorage, self).__init__(*args,
                                                            **new_kwargs)
            except TypeError:
                super(RandomFilenameStorage, self).__init__(*args, **kwargs)

        def get_available_name(self, name, retry=True):
            dir_name, file_name = os.path.split(name)
            file_root, file_ext = os.path.splitext(file_name)
            # If retry is True and the filename already exists, keep
            # on generating random filenames until the generated
            # filename doesn't exist.
            while True:
                file_prefix = random_string(self.randomfilename_length)
                # file_ext includes the dot.
                name = os.path.join(dir_name, file_prefix + file_ext)
                if not retry or not self.exists(name):
                    return name

        def _save(self, name, *args, **kwargs):
            while True:
                try:
                    return super(RandomFilenameStorage, self)._save(name,
                                                                    *args,
                                                                    **kwargs)
                except IOError, e:
                    if e.errno == EEXIST:
                        # We have a safe storage layer
                        if not self.randomfilename_uniquify_names:
                            # A higher storage layer will rename
                            raise
                        # Attempt to get_available_name() without retrying.
                        try:
                            name = self.get_available_name(name,
                                                           retry=False)
                        except TypeError:
                            warn('Could not call get_available_name() '
                                 'on %r with retry=False' % self)
                            name = self.get_available_name(name)
                    else:
                        raise


    RandomFilenameStorage.__name__ = 'RandomFilename' + storage_class.__name__
    return RandomFilenameStorage


RandomFilenameFileSystemStorage = RandomFilenameMetaStorage(
    storage_class=FileSystemStorage,
)
