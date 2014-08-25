from twisted.internet.defer import inlineCallbacks

from globaleaks.tests import helpers

from globaleaks.models import *
from globaleaks.settings import transact, transact_ro
from globaleaks.rest import errors
from globaleaks.utils.structures import Fields


class TestModels(helpers.TestGL):

    receiver_inc = 0

    @transact
    def context_add(self, store):
        c = self.localization_set(self.dummyContext, Context, 'en')
        context = Context(c)

        fo = Fields()
        fo.update_fields('en', self.dummyContext['fields'])
        fo.context_import(context)

        context.tags = self.dummyContext['tags']
        context.submission_timetolive = context.tip_timetolive = 1000
        context.description = context.name = \
            context.submission_disclaimer = \
            context.submission_introduction = {"en": u'Localized723'}
        store.add(context)
        return context.id

    @transact_ro
    def context_get(self, store, context_id):
        context = store.find(Context, Context.id == context_id).one()
        if context is None:
            return None
        return context.id

    @transact
    def context_del(self, store, context_id):
        context = store.find(Context, Context.id == context_id).one()
        if context is not None:
            store.remove(context)

    @transact
    def receiver_add(self, store):
        r = self.localization_set(self.dummyReceiver_1, Receiver, 'en')
        receiver_user = User(self.dummyReceiverUser_1)
        receiver_user.last_login = self.dummyReceiverUser_1['last_login']

        receiver_user.username = str(
            self.receiver_inc) + self.dummyReceiver_1['mail_address']
        receiver_user.password = self.dummyReceiverUser_1['password']
        store.add(receiver_user)

        receiver = Receiver(r)
        receiver.user = receiver_user
        receiver.gpg_key_status = Receiver._gpg_types[0]
        receiver.mail_address = self.dummyReceiver_1['mail_address']

        store.add(receiver)

        self.receiver_inc += 1

        return receiver.id

    @transact_ro
    def receiver_get(self, store, receiver_id):
        receiver = store.find(Receiver, Receiver.id == receiver_id).one()
        if receiver is None:
            return None
        return receiver.id

    @transact
    def receiver_del(self, store, receiver_id):
        receiver = store.find(Receiver, Receiver.id == receiver_id).one()
        if receiver is not None:
            store.remove(receiver)

    @transact
    def create_context_with_receivers(self, store):
        c = self.localization_set(self.dummyContext, Context, 'en')
        r = self.localization_set(self.dummyReceiver_1, Receiver, 'en')

        receiver_user1 = User(self.dummyReceiverUser_1)
        receiver_user1.last_login = self.dummyReceiverUser_1['last_login']

        receiver_user2 = User(self.dummyReceiverUser_1)
        receiver_user2.last_login = self.dummyReceiverUser_1['last_login']

        # Avoid receivers with the same username!
        receiver_user1.username = unicode("xxx")
        receiver_user2.username = unicode("yyy")

        store.add(receiver_user1)
        store.add(receiver_user2)

        context = Context(c)

        fo = Fields()
        fo.update_fields('en', self.dummyContext['fields'])
        fo.context_import(context)

        context.tags = self.dummyContext['tags']
        context.submission_timetolive = context.tip_timetolive = 1000
        context.description = context.name = \
            context.submission_disclaimer = \
            context.submission_introduction = {"en": u'Localized76w'}

        receiver1 = Receiver(r)
        receiver2 = Receiver(r)

        receiver1.user = receiver_user1
        receiver2.user = receiver_user2
        receiver1.gpg_key_status = receiver2.gpg_key_status = Receiver._gpg_types[
            0]
        receiver1.mail_address = receiver2.mail_address = 'x@x.it'

        context.receivers.add(receiver1)
        context.receivers.add(receiver2)

        store.add(context)

        return context.id

    @transact
    def create_receiver_with_contexts(self, store):
        c = self.localization_set(self.dummyContext, Context, 'en')
        r = self.localization_set(self.dummyReceiver_1, Receiver, 'en')

        receiver_user = User(self.dummyReceiverUser_1)
        receiver_user.last_login = self.dummyReceiverUser_1['last_login']

        # Avoid receivers with the same username!
        receiver_user.username = unicode("xxx")

        store.add(receiver_user)

        receiver = Receiver(r)
        receiver.user = receiver_user
        receiver.gpg_key_status = Receiver._gpg_types[0]
        receiver.mail_address = unicode('y@y.it')

        context1 = Context(c)

        fo = Fields()
        fo.update_fields('en', self.dummyContext['fields'])
        fo.context_import(context1)

        context1.tags = self.dummyContext['tags']
        context1.submission_timetolive = context1.tip_timetolive = 1000
        context1.description = context1.name = \
            context1.submission_disclaimer = \
            context1.submission_introduction = {"en": u'Valar Morghulis'}

        context2 = Context(c)

        fo.context_import(context2)

        context2.tags = self.dummyContext['tags']
        context2.submission_timetolive = context2.tip_timetolive = 1000
        context2.description = context2.name =\
            context2.submission_disclaimer = \
            context2.submission_introduction = {"en": u'Valar Dohaeris'}

        receiver.contexts.add(context1)
        receiver.contexts.add(context2)
        store.add(receiver)
        return receiver.id

    @transact_ro
    def list_receivers_of_context(self, store, context_id):
        context = store.find(Context, Context.id == context_id).one()
        receivers = []
        for receiver in context.receivers:
            receivers.append(receiver.id)
        return receivers

    @transact_ro
    def list_context_of_receivers(self, store, receiver_id):
        receiver = store.find(Receiver, Receiver.id == receiver_id).one()
        contexts = []
        for context in receiver.contexts:
            contexts.append(context.id)
        return contexts

    @transact
    def do_invalid_receiver_0length_name(self, store):
        self.dummyReceiver_1['name'] = ''
        Receiver(self.dummyReceiver_1)

    @transact
    def do_invalid_receiver_description_oversize(self, store):
        self.dummyReceiver_1['description'] = "A" * 5000
        Receiver(self.dummyReceiver_1)

    @inlineCallbacks
    def test_context_add_and_get(self):
        context_id = yield self.context_add()
        context_id = yield self.context_get(context_id)
        self.assertTrue(context_id is not None)

    @inlineCallbacks
    def test_context_add_and_del(self):
        context_id = yield self.context_add()
        yield self.context_del(context_id)
        context_id = yield self.context_get(context_id)
        self.assertTrue(context_id is None)

    @inlineCallbacks
    def test_receiver_add_and_get(self):
        receiver_id = yield self.receiver_add()
        receiver_id = yield self.receiver_get(receiver_id)
        self.assertTrue(receiver_id is not None)

    @inlineCallbacks
    def test_receiver_add_and_del(self):
        receiver_id = yield self.receiver_add()
        yield self.receiver_del(receiver_id)
        receiver_id = yield self.receiver_get(receiver_id)
        self.assertTrue(receiver_id is None)

    @inlineCallbacks
    def test_context_receiver_reference_1(self):
        context_id = yield self.create_context_with_receivers()
        receivers = yield self.list_receivers_of_context(context_id)
        self.assertEqual(2, len(receivers))

    @inlineCallbacks
    def test_context_receiver_reference_2(self):
        receiver_id = yield self.create_receiver_with_contexts()
        contexts = yield self.list_context_of_receivers(receiver_id)
        self.assertEqual(2, len(contexts))

    def test_invalid_receiver_0length_name(self):
        self.assertFailure(self.do_invalid_receiver_0length_name(),
                           errors.InvalidInputFormat)

    def test_invalid_receiver_description_oversize(self):
        self.assertFailure(self.do_invalid_receiver_description_oversize(),
                           errors.InvalidInputFormat)


class TestNextGenFields(helpers.TestGL):

    @transact
    def create_field(self, store):
        field_group = FieldGroup()
        field_group.x = 1
        field_group.y = 1
        field_group.label = "{'en': 'test label'}"
        field_group.description = "{'en': 'test description'}"
        field_group.hint = "{'en': 'test hint'}"
        field_group.multi_entry = True
        store.add(field_group)

        field = Field()
        field.preview = True
        field.required = False
        field.stats_enabled = True
        field.type = 'checkbox'
        field.regexp = '.*'
        field.options = {}
        field.default_value = 'foo'
        field.field_group = field_group

        store.add(field)

        return field.id

    def _find_one(self, store, model_name, model_id):
        from globaleaks import models
        model = getattr(models, model_name)
        return store.find(model, model.id == model_id).one()

    @transact
    def exists(self, store, model_name, model_id):
        return self._find_one(store, model_name, model_id) is not None

    @transact_ro
    def find(self, store, model_name, model_id, attr):
        m = self._find_one(store, model_name, model_id)
        if m is None:
            return None
        return getattr(m, attr)

    @transact
    def delete(self, store, model_name, model_id):
        m = self._find_one(store, model_name, model_id)
        store.remove(m)

    @inlineCallbacks
    def test_field_creation(self):
        field_id = yield self.create_field()
        exists = yield self.exists('Field', field_id)
        self.assertTrue(exists, "Field does not exist")

    @inlineCallbacks
    def test_delete_field(self):
        field_id = yield self.create_field()
        group_id = yield self.find('Field', field_id, 'group_id')
        yield self.delete('Field', field_id)

        exists = yield self.exists('Field', field_id)
        self.assertFalse(exists, "Field still exists")
        exists = yield self.exists('FieldGroup', group_id)
        self.assertFalse(exists, "FieldGroup still exists")

    test_delete_field.skip = "Still have to guarantee this kind of consistency"

    @inlineCallbacks
    def test_delete_field_group(self):
        field_id = yield self.create_field()
        group_id = yield self.find('Field', field_id, 'group_id')
        yield self.delete('FieldGroup', group_id)

        exists = yield self.exists('Field', field_id)
        self.assertFalse(exists, "Field still exists")

        exists = yield self.exists('FieldGroup', group_id)
        self.assertFalse(exists, "FieldGroup still exists")


class TestComposingFields(helpers.TestGLWithPopulatedDB):
    @inlineCallbacks
    def setUp(self):
        yield super(TestComposingFields, self).setUp()
        name_attrs = dict(
            label="{'en':'name'}",
            default_value=u'beppe',
            type=u'inputbox',
            regexp=u'',
            required=True,
            stats=False,
            preview=True,
        )
        surname_attrs = dict(
            label="{'en':'name'}",
            default_value=u'scamozza',
            type=u'inputbox',
            regexp=u'',
            required=True,
            stats=False,
            preview=True,
        )
        sex_attrs = dict(
            label="{'en':'name'}",
            default_value=u'none',
            type=u'radio',
            regexp=u'',
            required=True,
            stats=False,
            preview=True,
        )
        birthdate_attrs = dict(
            label="{'en':'name'}",
            default_value=u'01/01/1990',
            type=u'inputbox',
            regexp=u'',
            required=True,
            stats=True,
            preview=True,
        )
        generalities_attrs = dict(
            label="{'en': 'generalities'}"
        )

        self.name = yield Field.new(name_attrs)
        self.surname = yield Field.new(surname_attrs)
        self.sex = yield Field.new(sex_attrs)
        self.birthdate = yield Field.new(birthdate_attrs)
        self.generalities = yield FieldGroup.new(generalities_attrs,
                                                 self.name, self.surname)
    @inlineCallbacks
    def test_dataset(self):
        generalities = yield transact(lambda store:
            store.find(FieldGroup, FieldGroup.id == self.generalities).one()
        )()

        self.assertIsNotNone(generalities)

        generalities.add_children(self.sex, self.birthdate)

    @inlineCallbacks
    def test_serialize_field_group(self):
        serialized = yield FieldGroup.serialize(self.generalities)
        root_id = self.generalities
        children_id = (self.name, self.surname)

        self.assertEqual(serialized['id'], root_id)
        for child in serialized['_children']:
            self.assertIn(child['id'], children_id)

    @inlineCallbacks
    def test_step(self):
        context_id = yield self.dummyContext['id']
        Step.new(context_id, self.generalities)
