import os
import random
import string

from django.conf import settings
from django.core.files.storage import Storage, FileSystemStorage


CHARACTERS = string.lowercase + string.digits
DEFAULT_LENGTH = 16


def random_string(length):
    return ''.join(random.choice(CHARACTERS) for i in xrange(length))


def RandomFilenameMetaStorage(storage_class, length=None):
    class RandomFilenameStorage(storage_class):
        def __init__(self, *args, **kwargs):
            self.randomfilename_length = kwargs.pop('randomfilename_length',
                                                    length)
            if self.randomfilename_length is None:
                self.randomfilename_length = getattr(settings,
                                                     'RANDOM_FILENAME_LENGTH',
                                                     DEFAULT_LENGTH)
            super(RandomFilenameStorage, self).__init__(*args, **kwargs)

        def get_available_name(self, name):
            dir_name, file_name = os.path.split(name)
            file_root, file_ext = os.path.splitext(file_name)
            # If the filename already exists, keep on generating random
            # filenames until the generated filename doesn't exist.
            while True:
                file_prefix = random_string(self.randomfilename_length)
                # file_ext includes the dot.
                name = os.path.join(dir_name, file_prefix + file_ext)
                if not self.exists(name):
                    return name

    RandomFilenameStorage.__name__ = 'RandomFilename' + storage_class.__name__
    return RandomFilenameStorage


RandomFilenameFileSystemStorage = RandomFilenameMetaStorage(
    storage_class=FileSystemStorage,
)
