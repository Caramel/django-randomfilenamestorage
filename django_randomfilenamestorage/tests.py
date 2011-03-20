import re

from django.core.files.base import ContentFile
from django.test import TestCase

from django_randomfilenamestorage.storage import (
    RandomFilenameMetaStorage, RandomFilenameFileSystemStorage
)


class RandomFilenameTestCase(TestCase):
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
