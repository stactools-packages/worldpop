import logging

import click

from stactools.worldpop import stac

logger = logging.getLogger(__name__)


def create_worldpop_command(cli):
    """Creates the stactools-worldpop command line utility."""
    @cli.group(
        "worldpop",
        short_help=("Commands for working with stactools-worldpop"),
    )
    def worldpop():
        pass

    @worldpop.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    def create_collection_command(destination: str):
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection()

        collection.set_self_href(destination)

        collection.save_object()

        return None

    @worldpop.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    def create_item_command(source: str, destination: str):
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Collection
        """
        item = stac.create_item(source)

        item.save_object(dest_href=destination)

        return None

    return worldpop
