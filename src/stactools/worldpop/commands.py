import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, List

import click

from stactools.worldpop import cog
from stactools.worldpop.cog import download_create_cog
from stactools.worldpop.constants import API_URL, COLLECTIONS_METADATA
from stactools.worldpop.stac import create_collection, create_item
from stactools.worldpop.utils import get_iso3_list, get_metadata, get_popyears

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
                  type=click.Choice(list(COLLECTIONS_METADATA.keys())),
                  default="pop")
    @click.option(
        "-c",
        "--category",
        required=False,
        help="The category to create a STAC for within the chosen project.",
        type=click.Choice(
            sum([list(c.keys()) for c in COLLECTIONS_METADATA.values()], [])),
        default="wpgpunadj")
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC Collection json.",
    )
    @click.option("-k",
                  "--api_key",
                  required=False,
                  help="A WorldPop API key, required for >1000 calls per day.",
                  default="")
    @click.option(
        "-g",
        "--create_cog",
        help="Download and convert GeoTIFFs to COGs.",
        is_flag=True,
        default=False,
    )
    @click.option(
        "-t",
        "--tile",
        help="Tile the tiff into many smaller files.",
        is_flag=True,
        default=False,
    )
    @click.option(
        "-o",
        "--cog_destination",
        required=False,
        help="The output directory for tiles.",
    )
    def populate_collection_command(project: str, category: str,
                                    destination: str, api_key: str,
                                    create_cog: bool, tile: bool,
                                    cog_destination: str) -> Any:
        """Creates a collection for one WorldPop project/category and populates it with items.
        Args:
            project (str): WorldPop project ID.
            category (str): WorldPop category ID (member of `project`).
            destination (str): Directory used to store the STAC collections.
        """
        populate_collection_command_fn(project, category, destination, api_key,
                                       create_cog, tile, cog_destination)

    def populate_collection_command_fn(project: str, category: str,
                                       destination: str, api_key: str,
                                       create_cog: bool, tile: bool,
                                       cog_destination: str) -> Any:
        collection = create_collection(project, category)

        popyears = get_popyears(collection)
        iso3s = get_iso3_list(project, category)

        # Populate collection with items
        for i, iso3 in enumerate(iso3s, start=1):
            print(f"Creating items for iso3 {i}/{len(iso3s)}: {iso3}")
            metadata_url = f"{API_URL}/{project}/{category}?iso3={iso3}"
            if api_key != "":
                metadata_url += f"&key={api_key}"
            metadatas = get_metadata(metadata_url)["data"]

            for popyear in popyears:
                # Get the specific metadata for a popyear
                metadata_popyear = [
                    m for m in metadatas if m["popyear"] == popyear
                ]
                if len(metadata_popyear) == 0:
                    continue
                metadata = metadata_popyear[0]

                if create_cog:
                    cog_popyear_folder = os.path.join(cog_destination, project,
                                                      category, iso3, popyear)
                    # Download GeoTIFFs and create COGs, tiling if requested
                    cog_asset_folders = []
                    for tif_href in metadata["files"]:
                        # Create folder structure for COGs
                        cog_asset_name = os.path.basename(tif_href).replace(
                            ".tif", "")
                        cog_asset_folder = os.path.join(
                            cog_popyear_folder, cog_asset_name)
                        cog_asset_folders += [cog_asset_folder]
                        Path(cog_asset_folder).mkdir(parents=True,
                                                     exist_ok=True)
                        download_create_cog(output_directory=cog_asset_folder,
                                            retile=tile,
                                            access_url=tif_href.replace(
                                                "https://data", "ftp://ftp"))

                    # Get all (possibly tiled) cog file names, grouped by data asset
                    cog_items_hrefs = [
                        os.path.join(cog_asset_folder, cog_fname)
                        for cog_fname in os.listdir(cog_asset_folder)
                        for cog_asset_folder in cog_asset_folders
                    ]
                    # Transpose list of lists to group by tile instead
                    # See https://stackoverflow.com/questions/6473679/transpose-list-of-lists
                    cog_hrefs_items: List[Any] = list(
                        map(list, zip(*cog_items_hrefs)))

                    # Create an Item for each tile
                    for cog_hrefs in cog_hrefs_items:
                        item = create_item(project, category, iso3, popyear,
                                           metadatas, cog_hrefs)
                        if item is not None:
                            collection.add_item(item)

                else:
                    item = create_item(project, category, iso3, popyear,
                                       metadatas)
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
    @click.option("-k",
                  "--api_key",
                  required=False,
                  help="A WorldPop API key, required for >1000 calls per day.",
                  default="")
    @click.option(
        "-g",
        "--create_cog",
        help="Download and convert GeoTIFFs to COGs.",
        is_flag=True,
        default=False,
    )
    @click.option(
        "-t",
        "--tile",
        help="Tile the tiff into many smaller files.",
        is_flag=True,
        default=False,
    )
    @click.option(
        "-o",
        "--cog_destination",
        required=False,
        help="The output directory for tiles.",
    )
    def populate_all_collections_command(destination: str, api_key: str,
                                         create_cog: bool, tile: bool,
                                         cog_destination: str) -> Any:
        """Creates collections for all WorldPop projects/categories and populates them
         with items.
        Args:
            destination (str): Directory used to store the STAC collections.
        """
        proj_cats = [(p, c) for p, cs in COLLECTIONS_METADATA.items()
                     for c in cs.keys()]

        for project, category in proj_cats:
            populate_collection_command_fn(project, category, destination,
                                           api_key, create_cog, tile,
                                           cog_destination)

    @worldpop.command(
        "create-collection",
        short_help="Creates one STAC collection for worldpop data (no items).",
    )
    @click.option("-p",
                  "--project",
                  required=False,
                  help="The WorldPop project to create a STAC for.",
                  type=click.Choice(list(COLLECTIONS_METADATA.keys())),
                  default="pop")
    @click.option(
        "-c",
        "--category",
        required=False,
        help="The category to create a STAC for within the chosen project.",
        type=click.Choice(
            sum([list(c.keys()) for c in COLLECTIONS_METADATA.values()], [])),
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
                  help="The WorldPop project to create a STAC for.",
                  type=click.Choice(list(COLLECTIONS_METADATA.keys())),
                  default="pop")
    @click.option(
        "-c",
        "--category",
        required=False,
        help="The category to create a STAC for within the chosen project.",
        type=click.Choice(
            sum([list(c.keys()) for c in COLLECTIONS_METADATA.values()], [])),
        default="wpgpunadj")
    @click.option("-i",
                  "--iso3",
                  required=False,
                  help="The ISO3 of the country to create a STAC Item for.",
                  default="CHN")
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
    @click.option("-k",
                  "--api_key",
                  required=False,
                  help="A WorldPop API key, required for >1000 calls per day.",
                  default="")
    def create_item_command(project: str, category: str, iso3: str,
                            popyear: str, destination: str,
                            api_key: str) -> Any:
        """Creates a STAC Item for one project/category/iso3/popyear.

        Args:
            project (str): WorldPop project ID.
            category (str): WorldPop category ID (member of `project`).
            iso3 (str): ISO3 code for a country.
            popyear (str): Population year.
            destination (str): The output directory for the STAC json.
        """
        metadata_url = f"{API_URL}/{project}/{category}?iso3={iso3}"
        if api_key != "":
            metadata_url += f"&key={api_key}"
        metadatas = get_metadata(metadata_url)["data"]
        item = create_item(project, category, iso3, popyear, metadatas)
        if item is None:
            raise AssertionError("Item cannot be created for these inputs.")
        else:
            item_path = os.path.join(destination, f"{item.id}.json")
            item.set_self_href(item_path)
            item.make_asset_hrefs_relative()
            item.save_object()
            item.validate()

    @worldpop.command(
        "create-cog",
        short_help="Transform Geotiff to Cloud-Optimized Geotiff.",
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the COG",
    )
    @click.option(
        "-s",
        "--source",
        required=True,
        help="Path to an input GeoTiff",
    )
    @click.option(
        "-t",
        "--tile",
        help="Tile the tiff into many smaller files.",
        is_flag=True,
        default=False,
    )
    def create_cog_command(destination: str, source: str, tile: bool) -> None:
        """Generate a COG from a GeoTiff. The COG will be saved in the desination
        with `_cog.tif` appended to the name.

        Args:
            destination (str): Local directory to save output COGs
            source (str, optional): An input WorldPop GeoTiff
            tile (bool, optional): Tile the tiff into many smaller files
        """
        create_cog_command_fn(destination, source, tile)

    def create_cog_command_fn(destination: str, source: str,
                              tile: bool) -> None:
        if not os.path.isdir(destination):
            raise IOError(f'Destination folder "{destination}" not found')

        if source is None:
            cog.download_create_cog(destination, source, retile=tile)
        elif tile:
            cog.create_retiled_cogs(source, destination)
        else:
            output_path = os.path.join(
                destination,
                os.path.basename(source)[:-4] + "_cog.tif")
            cog.create_cog(source, output_path)

    return worldpop
