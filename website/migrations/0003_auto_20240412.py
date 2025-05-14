from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_alter_review_user'),
    ]
    operations = [
        migrations.AddField(
            model_name='order',
            name='plan',
            field=models.CharField(default='standard', max_length=50),
        ),
        migrations.AlterField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='website.order'),
        ),
    ]
