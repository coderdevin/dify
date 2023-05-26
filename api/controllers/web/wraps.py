# -*- coding:utf-8 -*-
import logging
import uuid
from datetime import datetime
from functools import wraps

from flask import request, session
from flask_restful import Resource
from werkzeug.exceptions import NotFound, Unauthorized

from extensions.ext_database import db
from libs import next_auth
from models.model import App, Site, EndUser

logger = logging.getLogger(__name__)


def validate_token(view=None):
    def decorator(view):
        @wraps(view)
        def decorated(*args, **kwargs):
            site = validate_and_get_site()

            app_model = db.session.query(App).get(site.app_id)
            if not app_model:
                raise NotFound()

            if app_model.status != 'normal':
                raise NotFound()

            if not app_model.enable_site:
                raise NotFound()

            validate_external_oauth_token(app_model)
            end_user = create_or_update_end_user_for_session(app_model)

            return view(app_model, end_user, *args, **kwargs)
        return decorated

    if view:
        return decorator(view)
    return decorator


def validate_and_get_site():
    """
    Validate and get API token.
    """
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        raise Unauthorized()

    auth_scheme, auth_token = auth_header.split(None, 1)
    auth_scheme = auth_scheme.lower()

    if auth_scheme != 'bearer':
        raise Unauthorized()

    site = db.session.query(Site).filter(
        Site.code == auth_token,
        Site.status == 'normal'
    ).first()

    if not site:
        raise NotFound()

    return site


def validate_external_oauth_token(app_model):
    auth_token = request.cookies.get('__Secure-next-auth.session-token')
    if not auth_token:
        raise Unauthorized()
    logger.debug(f"auth token received: {auth_token}, app_id: {app_model.id}, try deal next...")
    auth_user_info = None
    try:
        auth_user_info = next_auth.decrypt(auth_token)
    except Exception as e:
        logger.error(f"error decrypt external auth token, message: {str(e)}")

    if not auth_user_info or auth_user_info["exp"] and auth_user_info["exp"] < datetime.utcnow().timestamp():
        raise Unauthorized()
    logger.info(f"authorized user: {auth_user_info['name']} request app ({app_model.name})...")


def create_or_update_end_user_for_session(app_model):
    """
    Create or update session terminal based on session ID.
    """
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()

    session_id = session.get('session_id')
    end_user = db.session.query(EndUser) \
        .filter(
        EndUser.session_id == session_id,
        EndUser.type == 'browser'
    ).first()

    if end_user is None:
        end_user = EndUser(
            tenant_id=app_model.tenant_id,
            app_id=app_model.id,
            type='browser',
            is_anonymous=True,
            session_id=session_id
        )
        db.session.add(end_user)
        db.session.commit()

    return end_user


def generate_session_id():
    """
    Generate a unique session ID.
    """
    count = 1
    session_id = ''
    while count != 0:
        session_id = str(uuid.uuid4())
        count = db.session.query(EndUser) \
            .filter(EndUser.session_id == session_id).count()

    return session_id


class WebApiResource(Resource):
    method_decorators = [validate_token]
