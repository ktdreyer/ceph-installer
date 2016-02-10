import logging

from pecan import expose, request
from pecan.ext.notario import validate
from uuid import uuid4

from mariner.controllers import error
from mariner.tasks import install
from mariner import schemas
from mariner import models
from mariner import util

logger = logging.getLogger(__name__)


class OSDController(object):

    @expose('json')
    def index(self):
        # TODO: allow some autodiscovery here so that clients can see what is
        # available
        return dict()

    @expose(generic=True, template='json')
    def install(self):
        error(405)

    @install.when(method='POST', template='json')
    @validate(schemas.install_schema, handler="/errors/schema")
    def install_post(self):
        hosts = request.json.get('hosts')
        extra_vars = util.get_install_extra_vars(request.json)
        identifier = str(uuid4())
        task = models.Task(
            identifier=identifier,
            endpoint=request.path,
        )
        # we need an explicit commit here because the command may finish before
        # we conclude this request
        models.commit()
        kwargs = dict(extra_vars=extra_vars)
        install.apply_async(
            args=('osd', hosts, identifier),
            kwargs=kwargs,
        )

        return task

    @expose('json')
    def configure(self):
        return {}
