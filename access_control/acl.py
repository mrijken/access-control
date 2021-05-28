import dataclasses
from typing import List

from access_control import permission, permit, principal


@dataclasses.dataclass
class ACE:
    """An Entry in an access control list"""

    permit: permit.Permit
    principal: principal.Principal
    permission: permission.Permission


ACL = List[ACE]
