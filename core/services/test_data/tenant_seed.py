TENANT_DESCRIPTION_LENGTHS = {
  'population': ('none', 'short', 'medium', 'long',),
  'weights': (20, 40, 30, 10,),
}

TENANT_DESCRIPTION_TEMPLATES = {
  'none': (
    '',
  ),
  'short': (
    '{tenant_name} is a collaborative team.',
    '{tenant_name} is focused on practical execution.',
    '{tenant_name} supports a modern, distributed organization.',
  ),
  'medium': (
    '{tenant_name} is a collaborative organization focused on clear communication, practical execution, and steady improvement.',
    '{tenant_name} supports cross-functional teams working across planning, delivery, and day-to-day operations.',
    '{tenant_name} is a modern team that values simplicity, consistency, and sustainable growth.',
  ),
  'long': (
    '{tenant_name} is a collaborative organization focused on clear communication, practical execution, and steady improvement. '
    'The team works across planning, delivery, and operations, with an emphasis on transparency and maintainable processes. '
    'This workspace is used to support everyday coordination and continuous progress.',
    '{tenant_name} supports a modern, distributed team working across multiple functions and responsibilities. '
    'The organization values clarity, ownership, and reliable execution in daily work. '
    'Its workspace is intended to help members stay aligned, move efficiently, and keep information easy to find.',
    '{tenant_name} is a growing organization that brings together people from different roles and backgrounds. '
    'The team emphasizes practical collaboration, shared visibility, and a consistent operating rhythm. '
    'This tenant represents an active workspace for communication, coordination, and ongoing improvement.',
  ),
}
