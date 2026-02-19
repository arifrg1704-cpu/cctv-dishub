import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cctv_pontianak.settings")
django.setup()

from dashboard.models import CCTV

total = CCTV.objects.count()
valid = CCTV.objects.filter(latitude__isnull=False, longitude__isnull=False).count()

print(f"Total CCTV: {total}")
print(f"Valid GPS: {valid}")

if total == valid and total > 0:
    print("SUCCESS: Semua CCTV memiliki data GPS.")
else:
    print(f"WARNING: Masih ada {total - valid} CCTV tanpa GPS.")
