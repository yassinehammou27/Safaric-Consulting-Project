from django import template
# registers taglibrary 
register = template.Library() 
# creates the tag has_group, that can be used on templates to check user's groups. it will help identify permissions of a user
@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 
