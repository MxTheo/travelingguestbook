# aangepast load_old_data.py
import json
from django.utils.dateparse import parse_datetime
from streetactivity.models import Moment, StreetActivity

def load_old_moments():
    """Import old moments from a JSON-file"""
    with open('moments_data.json', 'r') as f:
        moments_data = json.load(f)
    
    for data in moments_data:
        try:
            # In je JSON heet het veld "activity", maar het is een ID
            activity_id = data['activity']
            activity = StreetActivity.objects.get(id=activity_id)
            
            # Maak nieuw Moment
            moment = Moment(
                activity=activity,
                report=data['report'],
                confidence_level=data['confidence_level'],
                from_practitioner=data['from_practitioner'],
                keywords=data['keywords']
            )
            
            # Behoud de originele datums
            if 'date_created' in data:
                moment.date_created = parse_datetime(data['date_created'])
            if 'date_modified' in data:
                moment.date_modified = parse_datetime(data['date_modified'])
            
            # Sla op zonder auto_now te triggeren
            moment.save(force_insert=True, force_update=False)
            
            print(f"✓ Geladen: {moment.id}")
            
        except StreetActivity.DoesNotExist:
            print(f"✗ Activiteit {data['activity']} niet gevonden voor moment {data.get('id', '?')}")
        except Exception as e:
            print(f"✗ Fout bij moment {data.get('id', '?')}: {str(e)}")

if __name__ == '__main__':
    load_old_moments()