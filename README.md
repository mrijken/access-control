# Access Control

With `access-control` you can manage access control list to check
wether a principal has access to a context with a certain permission.

## Concepts

### ACL (Access Control List)

An *ACL* is an ordered list of *ACE* (Access Control Entry). Every *Context* 
has an *ACL*.

### ACE (Access Control Entry)

An *ACE* consists of:
- a *Permit*
- a *Principal*
- a *Permission*

### Principal

A *Principal* represents an entity, typically a user or group.
This means that a typical user can have multiple principals, like `everyone`,
`userid:1234` and `group:admin`.

### Permit

The *Permit* is either ALLOW or DENY. This means that you can specify in the
*ACE* that a *Principal* has either to be denied of allowed access to the
*Context*.

### Context

The *Context* is a resource, like a page on a website, including the context of
that resource, like the folders in which the page is located.
Every context has an *ACL*.

### Permission

The *Permission* is the action like `view`, `change name`, `create user` on the *Context*.

### Matching

To get the *Permit* for a combination of *Context*, *Principal* and *Permission*,
the *ACL* of the context will be looked up (in the specified order). When there is
a match (based on *Principal* and *Permission*), the specified *Permit* (DENY
or ALLOW) is returned. When there is no match, the first match with *ACL* of the 
parent (like folders) will be returned.
When there is still no match, a DENY will be returned.

## Example

    >>> import access_control as ac
    >>> from typing import Optional

    Create some principals, next to the predefined ac.principal.everyone
    and ac.principal.authenticated.

    >>> user_1 = ac.principal.Principal('user:1')
    >>> group_admin = ac.principal.Principal('group:admin')

    Create some context. You can use predefined ObjectContext which can make a context 
    from any object.

    >>> class Page():
    ...     def __init__(self, name: str, parent: Optional["Page"]):
    ...         self.name = name
    ...         self.parent = parent

    >>> root_page = Page('root', None)
    >>> contact_page = Page('contact', root_page)

    >>> context_contact_page = ac.context.ObjectContext(contact_page)
    >>> context_root = ac.context.ObjectContext(root_page)

    Create permissions. For the contact page you can define a view and an edit permission

    >>> view_permission = ac.permission.Permission('view')
    >>> edit_permission = ac.permission.Permission('edit')

    Next we need to glue them together in acls.
    The context has a `acl` attribute which has the acl of the context *and* the parents of 
    the context. A subscription_list of the `subscribe` package will be used to
    get the acl of a certain context. You can subscribe one or more functions to 
    a subscription_list of the context. All acls will be combined in the order
    of the subscription_list.

    Only the admins can edit the page.

    >>> @context_contact_page.acl_subscription_list.subscribe()
    ... def get_acl(context):
    ...     return [ac.acl.ACE(ac.permit.Permit.ALLOW, group_admin, edit_permission)]

    And every can view everything.

    >>> @context_root.acl_subscription_list.subscribe()
    ... def get_acl(context):
    ...     return [ac.acl.ACE(ac.permit.Permit.ALLOW, ac.principal.everyone, view_permission)]
    
    When a user want to access the page for edit, we can ask whether the user is allowed.
    Therefor we need to know the principals of that user.

    >>> unauthenticated_user_principals = [ac.principal.everyone]
    >>> admin_user_princpals = {ac.principal.everyone, ac.principal.authenticated, user_1, group_admin}

    Both users can access the root and contact page with view permission

    >>> ac.context.get_permit(context_contact_page, admin_user_princpals, view_permission) == ac.permit.Permit.ALLOW
    True
    >>> ac.context.get_permit(context_root, admin_user_princpals, view_permission) == ac.permit.Permit.ALLOW
    True
    >>> ac.context.get_permit(context_contact_page, unauthenticated_user_principals, view_permission) == ac.permit.Permit.ALLOW
    True
    >>> ac.context.get_permit(context_root, unauthenticated_user_principals, view_permission) == ac.permit.Permit.ALLOW
    True


    The unauthenticated user has no edit permission to the contact page

    >>> ac.context.get_permit(context_contact_page, unauthenticated_user_principals, edit_permission) == ac.permit.Permit.DENY
    True

    The admin user does have access

    >>> ac.context.get_permit(context_contact_page, admin_user_princpals, edit_permission) == ac.permit.Permit.ALLOW
    True



