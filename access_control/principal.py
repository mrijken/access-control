import logging
from typing import Type

import subscribe

logger = logging.getLogger(__name__)


class Principal(str):
    pass


class PrincipalSubscriberList(subscribe.ClassSubscriptionList):
    # TODO check signature of subscribers (?? as single argument)
    def __init__(self, cls: Type):
        super().__init__(cls, "principal:")


everyone = Principal("system.Everyone")
authenticated = Principal("system.Authenticated")
