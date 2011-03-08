import re

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.test import TestCase

from django_randomfilenamestorage.storage import RandomFilenameMetaStorage


RandomFilenameStorage = RandomFilenameMetaStorage(FileSystemStorage)

class RandomFilenameTestCase(TestCase):
    def setUp(self):
        self.root_size = 16
        self.storage = RandomFilenameStorage(root_size=self.root_size)

    def test_get_available_name(self):
        name = self.storage.get_available_name('')
        self.assertTrue(re.match(r'[0-9a-z]{%d}$' % self.root_size, name),
                        '%r is invalid.' % name)
        name = self.storage.get_available_name('foo')
        self.assertTrue(re.match(r'[0-9a-z]{%d}$' % self.root_size, name),
                        '%r is invalid.' % name)
        name = self.storage.get_available_name('foo.txt')
        self.assertTrue(re.match(r'[0-9a-z]{%d}\.txt$' % self.root_size, name),
                        '%r is invalid.' % name)
        name = self.storage.get_available_name('foo/bar')
        self.assertTrue(re.match(r'foo/[0-9a-z]{%d}$' % self.root_size, name),
                        '%r is invalid.' % name)
        name = self.storage.get_available_name('foo/bar\.txt')
        self.assertTrue(re.match(r'foo/[0-9a-z]{%d}\.txt$' % self.root_size,
                                 name),
                        '%r is invalid.' % name)

    def test_save(self):
        name1 = self.storage.save('foo/bar\.txt', ContentFile('Hello world!'))
        self.storage.delete(name1)
        self.assertTrue(re.match(r'foo/[0-9a-z]{%d}\.txt$' % self.root_size,
                                 name1),
                        '%r is invalid.' % name1)
        name2 = self.storage.save('foo/bar\.txt', ContentFile('Hello world!'))
        self.storage.delete(name2)
        self.assertTrue(re.match(r'foo/[0-9a-z]{%d}\.txt$' % self.root_size,
                                 name2),
                        '%r is invalid.' % name2)
        self.assertNotEqual(name1, name2)
