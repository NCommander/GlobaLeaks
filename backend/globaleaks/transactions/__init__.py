# -*- coding: utf-8
"""
ORM Transactions definitions.
"""
from globaleaks import models
from globaleaks.orm import transact


def db_schedule_email(store, tid, address, subject, body):
    return models.db_forge_obj(store, models.Mail,
                               {
                                   'address': address,
                                   'subject': subject,
                                   'body': body,
                                   'tid': tid,
                               })

@transact
def schedule_email(store, tid, address, subject, body):
    return db_schedule_email(store, tid, address, subject, body)


@transact
def schedule_email_for_all_admins(store, subject, body):
    from globaleaks.handlers.admin.user import db_get_admin_users
    for user_desc in db_get_admin_users(store, 1):
        db_schedule_email(store, 1, user_desc['mail_address'], subject, body)
