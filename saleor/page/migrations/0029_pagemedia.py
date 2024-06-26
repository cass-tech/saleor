# Generated by Django 3.2.23 on 2024-03-23 12:53

from django.db import migrations, models
import django.db.models.deletion
import saleor.core.utils.json_serializer


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0028_add_default_page_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(db_index=True, editable=False, null=True)),
                ('private_metadata', models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='pages')),
                ('alt', models.CharField(blank=True, max_length=250)),
                ('type', models.CharField(choices=[('IMAGE', 'An uploaded image or an URL to an image'), ('VIDEO', 'A URL to an external video')], default='IMAGE', max_length=32)),
                ('external_url', models.CharField(blank=True, max_length=256, null=True)),
                ('oembed_data', models.JSONField(blank=True, default=dict)),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='media', to='page.page')),
            ],
            options={
                'ordering': ('sort_order', 'pk'),
            },
        ),
    ]
