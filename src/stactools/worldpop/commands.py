import itertools as it
import logging
import os
from datetime import datetime
from typing import Any

import click
from stactools.core.utils.convert import cogify

from stactools.worldpop.constants import COLLECTIONS_METADATA
from stactools.worldpop.stac import create_collection, create_item
from stactools.worldpop.utils import get_iso3_list, get_popyears

logger = logging.getLogger(__name__)


def create_worldpop_command(cli: Any) -> Any:
    """Creates the WorldPop STAC."""
    @cli.group(
        "worldpop",
        short_help=("Commands for working with WorldPop data."),
    )
    def worldpop() -> None:
        pass

    @worldpop.command(
        "populate-collection",
        short_help="Creates STAC collections for WorldPop data.",
    )
    @click.option("-p",
                  "--project",
                  required=False,
                  help="The WorldPop project to create a STAC for.",
                  type=click.Choice(COLLECTIONS_METADATA.values()),
                  default="pop")
    @click.option(
        "-c",
        "--category",
        required=False,
        help="The category to create a STAC for within the chosen project.",
        type=click.Choice(
            sum([c.keys() for c in COLLECTIONS_METADATA.values()], [])),
        default="wpgpunadj")
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Collection json.",
    )
    def populate_collection_command(project: str, category: str,
                                    destination: str) -> Any:
        """Creates a collection for one WorldPop project/category and populates it with items.
        Args:
            project (str): WorldPop project ID.
            category (str): WorldPop category ID (member of `project`).
            destination (str): Directory used to store the STAC collections.
        """
        collection = create_collection(project, category)

        popyears = get_popyears(collection)
        iso3s = get_iso3_list(project, category)

        # Populate collection with items
        iso3_popyears = list(it.product(iso3s, popyears))
        for i, (iso3, popyear) in enumerate(iso3_popyears, start=1):
            print(f"Creating item {i}/{len(iso3_popyears)}: {iso3}_{popyear}")
            item = create_item(project, category, iso3, popyear)
            if item is not None:
                collection.add_item(item)

        collection_dest = os.path.join(destination, collection.id)
        collection.normalize_hrefs(collection_dest)
        collection.save(dest_href=collection_dest)
        collection.validate()

    @worldpop.command(
        "populate-all-collections",
        short_help=(
            "Creates and populates all STAC collections for worldpop data.", ))
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC collections.",
    )
    def populate_all_collections_command(destination: str) -> Any:
        """Creates collections for all WorldPop projects/categories and populates them
         with items.
        Args:
            destination (str): Directory used to store the STAC collections.
        """
        proj_cats = [(p, c) for p, cs in COLLECTIONS_METADATA.items()
                     for c in cs.keys()]

        for project, category in proj_cats:
            collection = create_collection(project, category)

            popyears = get_popyears(collection)
            iso3s = get_iso3_list(project, category)

            # Populate collection with items
            iso3_popyears = list(it.product(iso3s, popyears))
            for i, (iso3, popyear) in enumerate(iso3_popyears, start=1):
                print(
                    f"Creating {project}/{category} item {i}/{len(iso3_popyears)}: {iso3}_{popyear}"
                )
                item = create_item(project, category, iso3, popyear)
                if item is not None:
                    collection.add_item(item)

            collection_dest = os.path.join(destination, collection.id)
            collection.normalize_hrefs(collection_dest)
            collection.save(dest_href=collection_dest)
            collection.validate()

    @worldpop.command(
        "create-collection",
        short_help="Creates one STAC collection for worldpop data (no items).",
    )
    @click.option("-p",
                  "--project",
                  required=False,
                  help="The WorldPop project to create a STAC for.",
                  type=click.Choice(COLLECTIONS_METADATA.values()),
                  default="pop")
    @click.option(
        "-c",
        "--category",
        required=False,
        help="The category to create a STAC for within the chosen project.",
        type=click.Choice(
            sum([c.keys() for c in COLLECTIONS_METADATA.values()], [])),
        default="wpgpunadj")
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Collection json.",
    )
    def create_collection_command(project: str, category: str,
                                  destination: str) -> Any:
        """Creates a STAC Collection for one WorldPop project/category.
        Args:
            project (str): WorldPop project ID.
            category (str): WorldPop category ID (member of `project`).
            destination (str): Directory used to store the STAC collection.
        """
        collection = create_collection(project, category)
        collection_dest = os.path.join(destination, collection.id)
        collection.normalize_hrefs(collection_dest)
        collection.save(dest_href=collection_dest)
        collection.validate()

    @worldpop.command(
        "create-item",
        short_help=(
            "Creates one STAC item for a given project, category and year.", ))
    @click.option("-p",
                  "--project",
                  required=False,
                  help="The WorldPop project to create a STAC Item for.",
                  type=click.Choice(COLLECTIONS_METADATA.values()),
                  default="pop")
    @click.option("-c",
                  "--category",
                  required=False,
                  help="The category to create a STAC Item for.",
                  type=click.Choice(
                      sum([c.keys() for c in COLLECTIONS_METADATA.values()],
                          [])),
                  default="wpgpunadj")
    @click.option("-y",
                  "--popyear",
                  required=False,
                  help="The year to create the STAC Item for.",
                  type=click.Choice(
                      [str(y) for y in range(2000,
                                             datetime.now().year)]),
                  default="2020")
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Item json.",
    )
    def create_item_command(project: str, category: str, iso3: str,
                            popyear: str, destination: str) -> Any:
        """Creates a STAC Item for one project/category/iso3/popyear.

        Args:
            project (str): WorldPop project ID.
            category (str): WorldPop category ID (member of `project`).
            iso3 (str): ISO3 code for a country.
            popyear (str): Population year.
            destination (str): The output directory for the STAC json.
        """
        item = create_item(project, category, iso3, popyear)
        if item is not None:
            item_path = os.path.join(destination, f"{item.id}.json")
            item.set_self_href(item_path)
            item.save_object()

    @worldpop.command(
        "create-cog",
        short_help="Transform Geotiff to Cloud-Optimized Geotiff.",
    )
    @click.option("-d",
                  "--destination",
                  required=True,
                  help="The output directory for the COG")
    @click.option("-s",
                  "--source",
                  required=True,
                  help="Path to an input GeoTiff")
    def create_cog_command(destination: str, source: str) -> None:
        """Generate a COG from a GeoTiff. The COG will be saved in the desination
        with `_cog.tif` appended to the name.

        Args:
            destination (str): Local directory to save output COGs
            source (str): An worldpop GeoTIFF
        """
        if not os.path.isdir(destination):
            raise IOError(f'Destination folder "{destination}" not found')

        output_path = os.path.join(destination,
                                   os.path.basename(source)[:-4] + "_cog.tif")

        args = ["-co", "OVERVIEWS=IGNORE_EXISTING"]

        cogify(source, output_path, args)

    return worldpop
