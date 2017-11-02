# -*- coding: utf-8 -*-
from globaleaks.handlers.admin import l10n as admin_l10n
from globaleaks.tests import helpers
from twisted.internet.defer import inlineCallbacks

empty_texts = {}

custom_texts = {
   '12345': '54321'
}

class TestAdminL10NHandler(helpers.TestHandler):
    _handler = admin_l10n.AdminL10NHandler

    @inlineCallbacks
    def test_get(self):
        handler = self.request(role='admin')

        response = yield handler.get(lang=u'en')

        self.assertEqual(response, {})

    @inlineCallbacks
    def test_put(self):
        check = yield admin_l10n.get(helpers.XTIDX, u'en')
        self.assertEqual(empty_texts, check)

        handler = self.request(custom_texts, role='admin')

        yield handler.put(lang=u'en')

        check = yield admin_l10n.get(helpers.XTIDX, u'en')
        self.assertEqual(custom_texts, check)

    @inlineCallbacks
    def test_delete(self):
        yield self.test_put()

        check = yield admin_l10n.get(helpers.XTIDX, u'en')
        self.assertEqual(custom_texts, check)

        handler = self.request({}, role='admin')
        handler.delete(lang=u'en')

        check = yield admin_l10n.get(helpers.XTIDX, u'en')
        self.assertEqual(empty_texts, check)
