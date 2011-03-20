from __future__ import with_statement

from contextlib import contextmanager

import re

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils.functional import LazyObject

from django_randomfilenamestorage.storage import (
    RandomFilenameMetaStorage, RandomFilenameFileSystemStorage
)


class StubStorage(object):
    def exists(*args, **kwargs):
        return False


class RandomFilenameTestCase(TestCase):
    def assertFilename(self, name, length=16):
        self.assertTrue(re.match(r'[0-9a-z]{%d}(?:\..+)?$' % length, name),
                        '%r is invalid.' % name)

    def test_init(self):
        StorageClass = RandomFilenameMetaStorage(storage_class=StubStorage)
        with patch(settings, RANDOM_FILENAME_LENGTH=NotImplemented):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''))
            storage = StorageClass(length=10)
            self.assertFilename(storage.get_available_name(''), length=10)
        with patch(settings, RANDOM_FILENAME_LENGTH=5):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''), length=5)
            storage = StorageClass(length=20)
            self.assertFilename(storage.get_available_name(''), length=20)

    def test_get_available_name(self):
        length = 16
        storage = RandomFilenameFileSystemStorage(length=length)
        name = storage.get_available_name('')
        self.assertTrue(re.match(r'[0-9a-z]{%d}$' % length, name),
                        '%r is invalid.' % name)
        name = storage.get_available_name('foo')
        self.assertTrue(re.match(r'[0-9a-z]{%d}$' % length, name),
                        '%r is invalid.' % name)
        name = storage.get_available_name('foo.txt')
        self.assertTrue(re.match(r'[0-9a-z]{%d}\.txt$' % length, name),
                        '%r is invalid.' % name)
        name = storage.get_available_name('foo/bar')
        self.assertTrue(re.match(r'foo/[0-9a-z]{%d}$' % length, name),
                        '%r is invalid.' % name)
        name = storage.get_available_name('foo/bar\.txt')
        self.assertTrue(re.match(r'foo/[0-9a-z]{%d}\.txt$' % length,
                                 name),
                        '%r is invalid.' % name)

    def test_save(self):
        length = 16
        storage = RandomFilenameFileSystemStorage(length=length)
        name1 = storage.save('foo/bar\.txt', ContentFile('Hello world!'))
        storage.delete(name1)
        self.assertTrue(re.match(r'foo/[0-9a-z]{%d}\.txt$' % length,
                                 name1),
                        '%r is invalid.' % name1)
        name2 = storage.save('foo/bar\.txt', ContentFile('Hello world!'))
        storage.delete(name2)
        self.assertTrue(re.match(r'foo/[0-9a-z]{%d}\.txt$' % length,
                                 name2),
                        '%r is invalid.' % name2)
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
