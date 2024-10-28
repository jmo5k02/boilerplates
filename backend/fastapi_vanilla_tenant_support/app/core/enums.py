from enum import StrEnum

class AppEnum(StrEnum):
    """
    A custom Enum class that extends StrEnum.
    """
    pass


class Visibility(AppEnum):
    open = "Open"
    restricted = "Restricted"


class UserRoles(AppEnum):
    owner = "owner"
    manager = "manager"
    admin = "admin"
    member = "member"