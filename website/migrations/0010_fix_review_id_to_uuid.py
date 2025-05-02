from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_fix_review_id_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False),
        ),
    ] 