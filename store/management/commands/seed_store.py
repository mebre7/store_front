from decimal import Decimal

from django.core.management.base import BaseCommand

from store.models import Collection, Product


class Command(BaseCommand):
    help = "Seed the store with demo catalog data."

    def handle(self, *args, **options):
        catalog = {
            "Everyday Essentials": [
                ("Organic Cotton Tee", "A breathable staple with a clean, structured fit.", "34.00", 84),
                ("Modular Daypack", "Weather-resistant carry with laptop storage and quick-access pockets.", "128.00", 32),
                ("Ceramic Travel Mug", "Double-wall mug for commute coffee and desk refills.", "28.00", 65),
            ],
            "Home Studio": [
                ("Walnut Desk Lamp", "Dimmable task lighting with a warm matte finish.", "96.00", 22),
                ("Cable Dock Pro", "Weighted desktop dock for chargers, earbuds, and adapters.", "42.00", 41),
                ("Linen Catchall Tray", "Soft-lined organizer for keys, cards, and daily carry.", "38.00", 58),
            ],
            "Performance": [
                ("Hydro Shell Jacket", "Packable rain shell with taped seams and ventilation.", "174.00", 18),
                ("Merino Trail Socks", "Moisture-managing socks for long workdays and weekend hikes.", "24.00", 120),
                ("Recovery Foam Roller", "Dense roller for mobility, warmups, and post-training recovery.", "44.00", 36),
            ],
        }

        created_products = 0
        for collection_title, products in catalog.items():
            collection, _ = Collection.objects.get_or_create(title=collection_title)
            for title, description, price, inventory in products:
                _, created = Product.objects.update_or_create(
                    slug=title.lower().replace(" ", "-"),
                    defaults={
                        "title": title,
                        "description": description,
                        "unit_price": Decimal(price),
                        "inventory": inventory,
                        "collection": collection,
                    },
                )
                created_products += int(created)

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Created {created_products} products."))
