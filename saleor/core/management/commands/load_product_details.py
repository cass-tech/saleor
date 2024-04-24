import os
import pandas as pd

from django.core.management import BaseCommand, call_command
from django.utils.text import slugify

from saleor.attribute.models import Attribute, AttributeValue, \
    AssignedProductAttributeValue
from saleor.channel.models import Channel
from saleor.product.models import ProductType, Category, Product, ProductChannelListing, \
    ProductVariant, ProductVariantChannelListing, Collection, CollectionProduct
from saleor.tests.utils import dummy_editorjs


class Command(BaseCommand):
    def get_row_data(self, sheet_dict: dict, columns: list, index: int):
        item_code = columns[0]
        collection_name = columns[1]
        classification = sheet_dict[collection_name][index]
        name_start = len("inspired by") if "inspired by" in classification.lower() else 0
        name_end = classification.lower().index("intense wood") \
            if "intense wood" in classification.lower() \
            else classification.lower().index("woody") \
            if "woody" in classification.lower() \
            else len(classification)
        product_variants = columns[6:]
        return {
            "name": classification[name_start:name_end].strip(),
            "item_code": sheet_dict[item_code][index],
            "description": f"{classification}. {sheet_dict['DESCRIPTION'][index]}",
            "notes": {
                "top": sheet_dict["TOP NOTES"][index].split(',') if pd.notna(
                    sheet_dict["TOP NOTES"][index]) else [],
                "middle": sheet_dict["MIDDEL NOTES"][index].split(
                    ',') if "MIDDEL NOTES" in columns and pd.notna(
                    sheet_dict["MIDDEL NOTES"][index]) else sheet_dict["MIDDLE NOTES"][
                    index].split(',') if "MIDDLE NOTES" in columns and pd.notna(
                    sheet_dict["MIDDLE NOTES"][index]) else [],
                "base": sheet_dict["BASE NOTES"][index].split(',') if pd.notna(
                    sheet_dict["BASE NOTES"][index]) else []
            },
            "variants": [
                {"sku": f"{sheet_dict[item_code][index]}-{cap.replace('ml', '')}",
                 "name": cap,
                 "price": sheet_dict[cap][index]} for cap in product_variants
            ]
        }

    def read_sheet(self, file_path: str):
        collections = []
        collection_products = {}
        xls = pd.ExcelFile(file_path)
        for sheet in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet, skiprows=1).rename(columns=lambda c: c.strip())
            columns = df.columns
            products = []
            collections.append(columns[1].strip())
            df_dict = df.to_dict()
            for r in range(0, len(df.index)):
                product_data = self.get_row_data(df_dict, columns, r)
                products.append(product_data)
            collection_products[columns[1].strip()] = products
        return collection_products

    def handle(self, *args, **options):
        call_command('loaddata', '/app/saleor/static/populatedb_data.json')
        file_path = os.path.join(os.getcwd(), 'saleor/static/Website products update 16-11 Thur.xlsx')
        collection_products = self.read_sheet(file_path)
        product_type = ProductType.objects.get(slug="perfume")
        default_channel = Channel.objects.get(slug="default-channel")
        perfume_category = Category.objects.get(slug='perfume')
        top_attribute = Attribute.objects.get(slug="top-note")
        mid_attribute = Attribute.objects.get(slug="mid-note")
        base_attribute = Attribute.objects.get(slug="base-note")
        notes = {
            "top": top_attribute,
            "middle": mid_attribute,
            "base": base_attribute
            }
        # category, _ = Category.objects.update_or_create(name=category_name,
        #                                              parent=perfume_category)
        for collection, products in collection_products.items():
            new_collection, _ = Collection.objects.update_or_create(
                name=collection,
                slug=slugify(collection)
            )
            for product in products:
                new_product, _ = Product.objects.update_or_create(
                    product_type=product_type,
                    category=perfume_category,
                    name=product['name'],
                    slug=slugify(f"{product['name']} {product['item_code']}"),
                    description=dummy_editorjs(product['description']),
                    description_plaintext=product['description'],
                    search_document=f"{product['name']}{product['description']}",
                )
                new_collection_product, _ = CollectionProduct.objects.update_or_create(
                    product=new_product,
                    collection=new_collection
                )
                for note, scents in product["notes"].items():
                    note_attribute = notes[note]
                    for scent in scents:
                        attribute_value, _ = AttributeValue.objects.update_or_create(
                            attribute=note_attribute, slug=slugify(scent))
                        attribute_value.name = scent.strip()
                        attribute_value.save()
                        product_attribute_value, _ = AssignedProductAttributeValue.objects.update_or_create(
                            value=attribute_value,
                            product=new_product
                        )
                product_listing, _ = ProductChannelListing.objects.update_or_create(
                    product=new_product,
                    channel=default_channel,
                    currency='ZAR'
                )
                for variant in product['variants']:
                    product_variant, _ = ProductVariant.objects.update_or_create(
                        product=new_product,
                        name=variant['name'],
                        sku=f"{variant['name']} {variant['sku']}"
                    )
                    variant_listing, _ = ProductVariantChannelListing.objects.update_or_create(
                        variant=product_variant,
                        channel=default_channel,
                        currency='ZAR',
                        price_amount=variant['price'],
                        discounted_price_amount=variant['price'],
                        cost_price_amount=0.6 * float(variant['price'])
                    )
