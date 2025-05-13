from django.contrib.auth.models import Group
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Generate groups'

    def handle(self, *args, **options):
        groups_names=['Admin','Vendor','Admin']
        created=[]

        for name in groups_names:
            group, was_created = Group.objects.get_or_create(name=name)

            if was_created:
                created.append(name)

        if created:
            self.stdout.write(self.style.SUCCESS(f"Groups created: {', '.join(created)}"))
        else:
            self.stdout.write(self.style.WARNING("All groups already exist."))