from datetime import datetime
import os
from typing import Any
import click
import logging
import itertools as it

from stactools.worldpop.stac import create_collection, create_item
from stactools.worldpop.constants import API_URL, COLLECTIONS_METADATA, PERIODS, GSDS, REGIONS, YEARS
from stactools.worldpop.utils import get_iso3_list
from stactools.core.utils.convert import cogify

logger = logging.getLogger(__name__)


def create_worldpop_command(cli: Any) -> Any:
    """Creates the North American Land Classification Monitoring System STAC."""
    @cli.group(
        "worldpop",
        short_help=("Commands for working with worldpop data."),
    )
    def worldpop() -> None:
        pass

    @worldpop.command(
        "populate-collection",
        short_help="Creates STAC collections for worldpop data.",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Collection json.",
    )
    def create_collection_command(dataset: str, subset:str, destination:str) -> Any:
        """Creates a STAC Collection for each mapped dataset from the North
        American Land Classification Monitoring System.
        Args:
            destination (str): Directory used to store the STAC collections.
        """
        collection = create_collection(dataset, subset)

        # Create popyears from temporal extent
        start, stop = collection.extent.temporal
        stop = stop if stop != None else datetime.now().year - 1
        popyears = range(int(start), int(stop)+1)

        # Get list of country codes
        iso3s = get_iso3_list(dataset, subset)

        # Populate collection with items
        for i, iso3 in enumerate(iso3s, start=1):
            for popyear in popyears:
                print(f"Creating item {i}/{len(iso3s)}: {iso3}")
                item = create_item(dataset, subset, iso3, str(popyear))
                collection.add_item(item)

        collection.normalize_hrefs(destination)
        collection.save()
        collection.validate()

    @worldpop.command(
        "create-collection",
        short_help="Creates STAC collections for worldpop data.",
    )
    @click.option(
        "-p",
        "--project",
        required=False,
        help="The WorldPop project to create a STAC for.",
        type=click.Choice(COLLECTIONS_METADATA.values()),
        default="pop"
    )
    @click.option(
        "-c",
        "--category",
        required=False,
        help="The category to create a STAC for within the chosen project.",
        type=click.Choice(sum([c.keys() for c in COLLECTIONS_METADATA.values()], [])),
        default="wpgpunadj"
        )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Collection json.",
    )
    def create_collection_command(project: str, category:str, destination:str) -> Any:
        """Creates a STAC Collection for each mapped dataset from the North
        American Land Classification Monitoring System.
        Args:
            destination (str): Directory used to store the STAC collections.
        """
        collection = create_collection(project, category)
        collection.normalize_hrefs(destination)
        collection.save()
        collection.validate()

    @worldpop.command(
        "create-item",
        short_help="Create a STAC item for a given region, GSD and year.",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC json.",
    )
    @click.option(
        "-s",
        "--source",
        required=False,
        help="The input COG to create the item from.",
        default=None,
    )
    @click.option("-r",
                  "--region",
                  required=False,
                  help="The region covered by the STAC Item.",
                  type=click.Choice(REGIONS.keys(), case_sensitive=False),
                  default="NA")
    @click.option("-g", "--gsd", required=False, type=click.Choice(GSDS), default="30")
    @click.option("-y",
                  "--year",
                  required=False,
                  help="The year or range of years covered by the STAC Item.",
                  type=click.Choice(list(set(sum(YEARS.values(), [])))),
                  default="2010-2015")
    def create_item_command((project: str, category: str, iso3: str, popyear: str, destination: str) -> Any:
        """Creates a STAC Item

        Args:
            destination (str): The output directory for the STAC json.
            source (str): The input COG to create the item from.
            region (str): The region covered by the STAC Item.
            gsd (int, float): The ground sampling distance of the STAC Item.
            year (str): The year or range of years covered by the STAC Item.
        """
        item = create_item(metadata_url)
        item_path = os.path.join(destination, f"{item.id}.json")
        item.set_self_href(item_path)
        item.save_object()

    @worldpop.command(
        "create-cog",
        short_help="Transform Geotiff to Cloud-Optimized Geotiff.",
    )
    @click.option("-d", "--destination", required=True, help="The output directory for the COG")
    @click.option("-s", "--source", required=True, help="Path to an input GeoTiff")
    def create_cog_command(destination: str, source: str) -> None:
        """Generate a COG from a GeoTiff. The COG will be saved in the desination
        with `_cog.tif` appended to the name.

        Args:
            destination (str): Local directory to save output COGs
            source (str): An input worldpop Landcover GeoTiff
        """
        if not os.path.isdir(destination):
            raise IOError(f'Destination folder "{destination}" not found')

        output_path = os.path.join(destination, os.path.basename(source)[:-4] + "_cog.tif")

        args = ["-co", "OVERVIEWS=IGNORE_EXISTING"]

        cogify(source, output_path, args)

    return worldpop
