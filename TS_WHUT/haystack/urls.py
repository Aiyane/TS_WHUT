# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url

from haystack.views import basic_search

urlpatterns = [
    url(r'^$', basic_search, name='haystack_search'),
]
