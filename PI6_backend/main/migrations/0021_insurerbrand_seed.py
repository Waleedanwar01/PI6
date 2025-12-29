from django.db import migrations

def seed_brands(apps, schema_editor):
    InsurerBrand = apps.get_model('main', 'InsurerBrand')
    defaults = [
        {'name': 'Progressive', 'hover_color': '#00a3e0'},
        {'name': 'Safeco', 'hover_color': '#eeb900'},
        {'name': 'Allstate', 'hover_color': '#0055ff'},
        {'name': 'American Modern', 'hover_color': '#003366'},
        {'name': 'National General', 'hover_color': '#c41230'},
        {'name': 'Chubb', 'hover_color': '#231f20'},
    ]
    for item in defaults:
        InsurerBrand.objects.get_or_create(name=item['name'], defaults={'hover_color': item['hover_color'], 'is_active': True})

def unseed_brands(apps, schema_editor):
    InsurerBrand = apps.get_model('main', 'InsurerBrand')
    InsurerBrand.objects.filter(name__in=[
        'Progressive', 'Safeco', 'Allstate', 'American Modern', 'National General', 'Chubb'
    ]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_insurerbrand'),
    ]

    operations = [
        migrations.RunPython(seed_brands, reverse_code=unseed_brands),
    ]
