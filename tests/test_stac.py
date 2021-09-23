import unittest

from stactools.worldpop import stac


class StacTest(unittest.TestCase):
    def test_create_collection(self):
        project = "pop"
        category = "wpgpunadj"
        collection = stac.create_collection(project, category)
        collection.set_self_href("")

        # Check that it has some required attributes
        self.assertEqual(collection.id, f"{project}_{category}")
        self.assertEqual(collection.license, "CC-BY-4.0")
        self.assertEqual(collection.extra_fields["sci:doi"],
                         "10.5258/SOTON/WP00660")
        self.assertEqual(len(collection.extra_fields["item_assets"]), 3)
        self.assertEqual(collection.summaries.lists["gsd"], [100.0])

        # Validate
        collection.validate()

    def test_create_item(self):
        project = "pop"
        category = "wpgpunadj"
        iso3 = "CHN"
        popyear = "2020"
        item = stac.create_item(project, category, iso3, popyear)

        # Check that it has some required attributes
        self.assertEqual(item.id, f"{iso3}_{popyear}")
        self.assertEqual(item.properties["gsd"], 100.0)
        self.assertEqual(item.properties["sci:doi"], '10.5258/SOTON/WP00660')
        self.assertEqual(item.properties["proj:epsg"], 4326)
        self.assertEqual(len(item.assets), 3)

        # Validate
        item.validate()
