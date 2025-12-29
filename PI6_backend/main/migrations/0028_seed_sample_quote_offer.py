from django.db import migrations

def seed_sample_offer(apps, schema_editor):
    SiteConfiguration = apps.get_model('main', 'SiteConfiguration')
    InsurerBrand = apps.get_model('main', 'InsurerBrand')
    QuoteOffer = apps.get_model('main', 'QuoteOffer')
    phone = None
    try:
        cfg = SiteConfiguration.objects.first()
        if cfg and cfg.site_phone:
            phone = cfg.site_phone
    except Exception:
        pass
    offer, created = QuoteOffer.objects.get_or_create(
        title='Sample Homeowners Offer',
        defaults={
            'premium': '$97/mo',
            'phone': phone or '1-888-547-1451',
            'cta_text': 'Call Now',
            'highlight': 'Save $50',
            'notes': 'By clicking Call, you agree to our terms and consent policy.',
            'order': 1,
            'is_active': True,
        }
    )
    # Attach up to 3 known brands if they exist
    brand_names = ['Allstate', 'Progressive', 'State Farm', 'Safeco', 'Travelers']
    for name in brand_names:
        b = InsurerBrand.objects.filter(name__iexact=name).first()
        if b:
            offer.brands.add(b)

def unseed_sample_offer(apps, schema_editor):
    QuoteOffer = apps.get_model('main', 'QuoteOffer')
    QuoteOffer.objects.filter(title='Sample Homeowners Offer').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_remove_quoteoffer_brand_quoteoffer_brands'),
    ]

    operations = [
        migrations.RunPython(seed_sample_offer, unseed_sample_offer),
    ]
