"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import uuid

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from .models import get_user_email
from .common import db, session, T, cache, auth, signed_url


url_signer = URLSigner(session)

# The auth.user below forces login.
@action('index')
@action.uses('index.html', auth.user)
def index():
    rows = db(db.address.user_email == get_user_email()).select()

    for row in rows:
        phone_str = ""
        phone_numbers = db(db.phone.address_id == row.id).select()
        for phone_number in phone_numbers:
            number = phone_number.phone_number
            kind = phone_number.kind
            if phone_str != "":
                phone_str += ", "
            phone_str += f"{number} ({kind})"

        db(db.address.id == row.id).update(phone=phone_str)

    return dict(rows=rows)


@action('add', method=["GET", "POST"])
@action.uses('add.html', url_signer, db, session, auth.user)
def add():
    form = Form(db.address, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)


@action('del_address/<address_id:int>')
@action.uses(db, auth.user, session, url_signer)
def del_address(address_id=None):
    assert address_id is not None
    db(db.address.id == address_id).delete()
    redirect(URL('index'))


@action('edit_address/<address_id:int>', method=["GET", "POST"])
@action.uses('add.html', url_signer, db, session, auth.user)
def edit_address(address_id=None):
    assert address_id is not None

    p = db.address[address_id]
    if p is None:
        redirect(URL('index'))
    if p.user_email != get_user_email():
        redirect(URL('index'))

    form = Form(db.address, record=p, deletable=False,
                csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)


@action('edit_phones/<address_id:int>')
@action.uses('edit_phones.html', url_signer, db, session, auth.user)
def edit_phones(address_id=None):
    assert address_id is not None

    return dict(
        entry=db(db.address.id == address_id).select(),
        address_id=address_id,
        rows=db(db.phone.address_id == address_id).select()
    )


@action('add_phone/<address_id:int>', method=["GET", "POST"])
@action.uses('add_phone.html', url_signer, db, session, auth.user)
def add_phone(address_id=None):
    assert address_id is not None
    form = Form([Field('phone'), Field('kind')], csrf_session=session,
                formstyle=FormStyleBulma)

    if form.accepted:
        db.phone.insert(address_id=address_id,
                        phone_number=form.vars['phone'], kind=form.vars['kind'])
        redirect(URL('edit_phones/' + str(address_id)))

    return dict(
        entry=db(db.address.id == address_id).select(),
        form=form)


@action('del_phone/<address_id:int>/<phone_id:int>')
@action.uses(db, auth.user, session, url_signer)
def del_phone(phone_id=None, address_id=None):
    assert phone_id is not None
    assert address_id is not None
    db(db.phone.id == phone_id).delete()
    redirect(URL('edit_phones/' + str(address_id)))


@action('edit_phone/<address_id:int>/<phone_id:int>', method=["GET", "POST"])
@action.uses('add_phone.html', db, auth.user, session, url_signer)
def edit_phone(phone_id=None, address_id=None):
    assert phone_id is not None
    assert address_id is not None

    p = db.phone[phone_id]
    if p is None:
        redirect(URL('edit_phone/<address_id:int>/<phone_id:int>'))

    form = Form(db.phone, record=p, deletable=False,
                csrf_session=session, formstyle=FormStyleBulma)

    if form.accepted:
        redirect(URL('edit_phones/' + str(address_id)))

    return dict(form=form,
                entry=db(db.address.id == address_id).select())
