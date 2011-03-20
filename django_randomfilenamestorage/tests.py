from __future__ import with_statement

from contextlib import contextmanager

import posixpath
import re

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils.functional import LazyObject

from django_randomfilenamestorage.storage import (
    RandomFilenameMetaStorage, RandomFilenameFileSystemStorage,
    DEFAULT_LENGTH
)


class StubStorage(object):
    def exists(*args, **kwargs):
        return False


class RandomFilenameTestCase(TestCase):
    def assertFilename(self, name, original, length=DEFAULT_LENGTH):
        dirname, pathname = posixpath.split(original)
        if dirname:
            dirname += posixpath.sep
        root, ext = posixpath.splitext(pathname)
        regexp = re.compile(r'%s[0-9a-z]{%d}%s$' % (re.escape(dirname),
                                                    length,
                                                    re.escape(ext)))
        self.assertTrue(regexp.match(name), '%r is invalid.' % name)

    def test_class(self):
        StorageClass = RandomFilenameMetaStorage(storage_class=StubStorage)
        with patch(settings, RANDOM_FILENAME_LENGTH=NotImplemented):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''), '')
        StorageClass = RandomFilenameMetaStorage(storage_class=StubStorage,
                                                 length=5)
        with patch(settings, RANDOM_FILENAME_LENGTH=NotImplemented):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''), '', length=5)
            storage = StorageClass(randomfilename_length=10)
            self.assertFilename(storage.get_available_name(''), '', length=10)

    def test_init(self):
        StorageClass = RandomFilenameMetaStorage(storage_class=StubStorage)
        with patch(settings, RANDOM_FILENAME_LENGTH=NotImplemented):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''), '')
            storage = StorageClass(randomfilename_length=10)
            self.assertFilename(storage.get_available_name(''), '', length=10)
        with patch(settings, RANDOM_FILENAME_LENGTH=5):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''), '', length=5)
            storage = StorageClass(randomfilename_length=20)
            self.assertFilename(storage.get_available_name(''), '', length=20)

    def test_get_available_name(self):
        storage = RandomFilenameFileSystemStorage(
            randomfilename_length=DEFAULT_LENGTH
        )
        self.assertFilename(storage.get_available_name(''), '')
        self.assertFilename(storage.get_available_name('foo'), 'foo')
        self.assertFilename(storage.get_available_name('foo.txt'), 'foo.txt')
        self.assertFilename(storage.get_available_name('foo/bar'), 'foo/bar')
        self.assertFilename(storage.get_available_name('foo/bar.txt'),
                            'foo/bar.txt')

    def test_save(self):
        storage = RandomFilenameFileSystemStorage(
            randomfilename_length=DEFAULT_LENGTH
        )
        name1 = storage.save('foo/bar.txt', ContentFile('Hello world!'))
        storage.delete(name1)
        self.assertFilename(name1, 'foo/bar.txt')
        name2 = storage.save('foo/bar.txt', ContentFile('Hello world!'))
        storage.delete(name2)
        self.assertFilename(name2, 'foo/bar.txt')
        self.assertNotEqual(name1, name2)


@contextmanager
def patch(namespace, **values):
    """Patches `namespace`.`name` with `value` for (name, value) in values"""
    originals = {}
    if isinstance(namespace, LazyObject):
        if namespace._wrapped is None:
            namespace._setup()
        namespace = namespace._wrapped
    for (name, value) in values.iteritems():
        try:
            originals[name] = getattr(namespace, name)
        except AttributeError:
            originals[name] = NotImplemented
        if value is NotImplemented:
            if originals[name] is not NotImplemented:
                delattr(namespace, name)
        else:
            setattr(namespace, name, value)
    try:
        yield
    finally:
        for (name, original_value) in originals.iteritems():
            if original_value is NotImplemented:
                if values[name] is not NotImplemented:
                    delattr(namespace, name)
            else:
                setattr(namespace, name, original_value)
