import enum


class Permit(enum.Enum):
    """
    The Permit to take when there is a match between context, principal and permission.
    """

    ALLOW = "allow"
    DENY = "deny"
