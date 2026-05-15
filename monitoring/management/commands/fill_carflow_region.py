import random
from django.core.management.base import BaseCommand
from directory.models import Region
from monitoring.models import CarFlow


class Command(BaseCommand):
    help = "region_soato=NULL bo'lgan CarFlow larni to'ldiradi (1726 = 70%)"

    def handle(self, *args, **options):
        qs = CarFlow.objects.all()
        total = qs.count()

        if total == 0:
            self.stdout.write("CarFlow topilmadi.")
            return

        other_soatos = list(
            Region.objects
            .exclude(code='1726')
            .exclude(code__isnull=True)
            .exclude(code='0')
            .values_list('code', flat=True)
        )
        other_soatos = [int(c) for c in other_soatos if str(c).isdigit() and int(c) > 0]

        def pick():
            if random.random() < 0.70:
                return 1726
            return random.choice(other_soatos)

        updated = 0
        batch = []
        for flow in qs.iterator(chunk_size=500):
            flow.region_soato = pick()
            batch.append(flow)
            if len(batch) == 500:
                CarFlow.objects.bulk_update(batch, ['region_soato'])
                updated += len(batch)
                batch = []

        if batch:
            CarFlow.objects.bulk_update(batch, ['region_soato'])
            updated += len(batch)

        self.stdout.write(self.style.SUCCESS(f"{updated} ta CarFlow yangilandi."))
