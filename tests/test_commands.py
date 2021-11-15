import os.path
from tempfile import TemporaryDirectory

import pystac
from stactools.testing import CliTestCase

from stactools.worldpop.commands import create_worldpop_command
from tests import test_data


class CommandsTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_worldpop_command]

    def test_create_collection(self):
        with TemporaryDirectory() as tmp_dir:
            collection_dest = os.path.join(tmp_dir, "pop_wpgpunadj")

            result = self.run_command(
                ["worldpop", "create-collection", "-d", tmp_dir])

            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

            jsons = [
                p for p in os.listdir(collection_dest) if p.endswith(".json")
            ]
            self.assertEqual(len(jsons), 1)

            collection = pystac.read_file(
                os.path.join(collection_dest, jsons[0]))
            self.assertEqual(collection.id, "pop_wpgpunadj")
            self.assertEqual(collection.license, "CC-BY-4.0")
            self.assertEqual(collection.extra_fields["sci:doi"],
                             "10.5258/SOTON/WP00660")
            self.assertEqual(len(collection.extra_fields["item_assets"]), 3)
            self.assertEqual(collection.summaries.lists["gsd"], [100.0])

            collection.validate()

    def test_create_item(self):
        with TemporaryDirectory() as tmp_dir:
            test_path = test_data.get_path("data-files")
            cog_path = os.path.join(test_path, [
                d for d in os.listdir(test_path) if d.lower().endswith(".tif")
            ][0])
            result = self.run_command(
                ["worldpop", "create-item", "-d", tmp_dir, "-o", cog_path])
            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item = pystac.read_file(os.path.join(tmp_dir, jsons[0]))
            self.assertEqual(item.id, "ABW_2020")
            self.assertEqual(item.properties["gsd"], 100.0)
            self.assertEqual(item.properties["sci:doi"],
                             "10.5258/SOTON/WP00685")
            self.assertEqual(item.properties["proj:epsg"], 4326)
            self.assertEqual(len(item.assets), 3)

            item.validate()

    def test_create_cog(self):
        with TemporaryDirectory() as tmp_dir:
            test_path = test_data.get_path("data-files")
            paths = [
                os.path.join(test_path, d) for d in os.listdir(test_path)
                if d.lower().endswith(".tif")
            ]

            for path in paths:
                result = self.run_command(
                    ["worldpop", "create-cog", "-d", tmp_dir, "-s", path])
                self.assertEqual(result.exit_code,
                                 0,
                                 msg="\n{}".format(result.output))

                cogs = [
                    p for p in os.listdir(tmp_dir) if p.endswith("_cog.tif")
                ]
                self.assertEqual(len(cogs), 1)
