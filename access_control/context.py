from typing import List, Optional, Type

import subscribe

from access_control import permission, principal
from access_control.acl import ACL
from access_control.permit import Permit


class ContextSubscriberList(subscribe.ClassSubscriptionList):
    # TODO check signature of subscribers (context as single argument)
    def __init__(self, cls: Type):
        super().__init__(cls, "context:")


class ContextBase:
    """
    A context is the identification of a resource for which access is managed.
    """

    def __init__(self, acl_subscription_list: subscribe.SubscriptionList) -> None:
        self.acl_subscription_list = acl_subscription_list

    @property
    def parent(self) -> Optional["ContextBase"]:
        """Get the parent of the context. This is usefull when access
        have to be inherited from the parent"""
        return None

    @property
    def context_acl(self) -> ACL:
        """
        Default implementation of getting the acl of this context
        (without the context of any parent).

        This implementation will iterate over subscribers to the context.

        Override this in a Context subclass when appropriate.
        """
        acl: ACL = []
        for subscriber in self.acl_subscription_list.subscribers:
            acl.extend(subscriber(self))

        return acl

    @property
    def acl(self) -> ACL:
        """Get the ACL for this context, starting with the acl of the context
        and next the acl of the parent (which can include their parent acl recursively)
        """
        return self.context_acl + (self.parent.acl if self.parent else [])

    def __repr__(self) -> str:
        return f"<Context id:{id(self)}>"


class PathContext(ContextBase):
    """
    A PathContext if a Context which is based on the hierarchy of an url path, where
    access can be inherited from the folder in which the page is located.
    """

    def __init__(self, path: str) -> None:
        self.path = path.rstrip("/") or "/"
        super().__init__(acl_subscription_list=subscribe.SubscriptionList("context_acl:" + self.path))

    @property
    def parent(self) -> Optional["ContextBase"]:
        """
        >>> p = PathContext("/user/123/info")
        >>> p.path
        '/user/123/info'
        >>> p.parent
        <PathContext path:/user/123>
        >>> p.parent.path
        '/user/123'

        >>> p = PathContext("/user")
        >>> p.path
        '/user'
        >>> p.parent
        <PathContext path:/>
        >>> p.parent.path
        '/'

        >>> p = PathContext("/")
        >>> p.path
        '/'
        >>> p.parent is None
        True

        """
        if self.path == "/":
            return None

        return self.__class__("/".join(self.path.split("/")[:-1]))

    def __repr__(self) -> str:
        return f"<PathContext path:{self.path}>"


class ObjectContext(ContextBase):
    parent_attribute_name = "parent"

    def __init__(self, obj):
        self.obj = obj
        super().__init__(acl_subscription_list=subscribe.SuperClassSubscriptionList(self.obj.__class__, "context_acl:"))

    @property
    def parent(self) -> Optional[ContextBase]:
        parent_object = getattr(self.obj, self.parent_attribute_name, None)
        return self.__class__(parent_object) if parent_object else None


def get_permit(
    context: ContextBase, principals: List[principal.Principal], permission_: permission.Permission
) -> Permit:
    """
    Returns the Permit (Permit) for the first match acl with the `principals`,  `permission` and `context`.

    Returns Permit.DENY when there is no match
    """

    for ace in context.acl:
        if ace.principal in principals and permission_ == ace.permission:
            return ace.permit

    return Permit.DENY
