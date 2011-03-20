import os
import random
import string

from django.conf import settings
from django.core.files.storage import Storage, FileSystemStorage


def random_string(length):
    return ''.join(random.sample(string.lowercase + string.digits, length))


def RandomFilenameMetaStorage(storage_class):
    class RandomFilenameStorage(storage_class):
        def __init__(self, *args, **kwargs):
            self.length = kwargs.pop('length', None)
            if self.length is None:
                self.length = getattr(settings, 'RANDOM_FILENAME_LENGTH', 16)
            super(RandomFilenameStorage, self).__init__(*args, **kwargs)

        def get_available_name(self, name):
            dir_name, file_name = os.path.split(name)
            file_root, file_ext = os.path.splitext(file_name)
            # If the filename already exists, keep on generating random
            # filenames until the generated filename doesn't exist.
            while True:
                file_prefix = random_string(self.length)
                # file_ext includes the dot.
                name = os.path.join(dir_name, file_prefix + file_ext)
                if not self.exists(name):
                    return name

    RandomFilenameStorage.__name__ = 'RandomFilename' + storage_class.__name__
    return RandomFilenameStorage


RandomFilenameFileSystemStorage = RandomFilenameMetaStorage(
    storage_class=FileSystemStorage,
)
