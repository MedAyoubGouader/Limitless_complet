from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_create_review_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='id',
            field=models.AutoField(primary_key=True),
        ),
    ] 