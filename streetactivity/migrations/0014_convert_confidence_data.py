# streetactivity/migrations/0014_convert_confidence_data.py
from django.db import migrations

def convert_confidence_values(apps, schema_editor):
    Moment = apps.get_model('streetactivity', 'Moment')
    
    confidence_mapping = {
        'pioneer': 0,
        'intermediate': 1,
        'climax': 2,
    }
    
    print("📊 Converting confidence_level values...")
    
    converted = 0
    for moment in Moment.objects.all():
        old_value = moment.confidence_level
        
        if old_value in confidence_mapping:
            new_value = confidence_mapping[old_value]
            moment.confidence_level = new_value
            moment.save(update_fields=['confidence_level'])
            converted += 1
    
    print(f"✅ Converted {converted}/{Moment.objects.count()} records")
    
    # Simpele distributie check
    print("\nDistributie na conversie:")
    for value, label in [(0, 'onzeker'), (1, 'tussenin'), (2, 'zelfverzekerd')]:
        count = Moment.objects.filter(confidence_level=value).count()
        print(f"  {label} ({value}): {count} records")

def reverse_conversion(apps, schema_editor):
    Moment = apps.get_model('streetactivity', 'Moment')
    
    reverse_mapping = {
        0: 'pioneer',
        1: 'intermediate',
        2: 'climax',
    }
    
    print("↩️ Reverting confidence_level values...")
    
    for moment in Moment.objects.all():
        if moment.confidence_level in reverse_mapping:
            moment.confidence_level = reverse_mapping[moment.confidence_level]
            moment.save(update_fields=['confidence_level'])
    
    print("✅ Reversion complete!")

class Migration(migrations.Migration):
    dependencies = [
        ('streetactivity', '0013_alter_moment_options_moment_order_experience_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_confidence_values, reverse_conversion),
    ]