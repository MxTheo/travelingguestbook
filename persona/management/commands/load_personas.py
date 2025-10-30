import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from persona.models import Persona, Problem, Reaction


class Command(BaseCommand):
    """Django management command to load personas from a JSON file."""
    help = 'Load personas data from JSON fixture'

    def add_arguments(self, parser):
        """Add command line arguments for the management command."""
        parser.add_argument(
            '--file_path',
            type=str,
            default='persona/fixtures/personas.json',
            help='Path to the JSON file relative to project root'
        )

    def handle(self, *args, **options):
        """Handle the command to load personas from the specified JSON file."""
        file_path = options['file_path']
        
        # Bouw het volledige pad
        full_path = os.path.join(settings.BASE_DIR, file_path)
        
        self.stdout.write(f"Loading personas from: {full_path}")
        
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                personas_data = json.load(file)
                
                for persona_data in personas_data:
                    # Check of persona al bestaat
                    persona, created = Persona.objects.get_or_create(
                        title=persona_data['title'],
                        defaults={
                            'description': persona_data['description'],
                            'core_question': persona_data['core_question']
                        }
                    )
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"Created persona: {persona.title}")
                        )
                        
                        # Voeg problemen toe
                        for problem_data in persona_data['problems']:
                            Problem.objects.create(
                                persona=persona,
                                description=problem_data['description']
                            )
                        
                        # Voeg reacties toe
                        for reaction_data in persona_data['reactions']:
                            Reaction.objects.create(
                                persona=persona,
                                description=reaction_data['description']
                            )
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"Added problems and reactions for: {persona.title}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"Persona already exists: {persona.title}")
                        )
                
                self.stdout.write(
                    self.style.SUCCESS("Successfully loaded all personas!")
                )
                
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"File not found: {full_path}")
            )
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f"Invalid JSON file: {e}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"An error occurred: {e}")
            )
