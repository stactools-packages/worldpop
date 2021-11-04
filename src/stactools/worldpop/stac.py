import logging
import os
from typing import Any, List, Union

import rasterio
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    MediaType,
    SpatialExtent,
    TemporalExtent,
)
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.projection import (
    ProjectionExtension,
    SummariesProjectionExtension,
)
from pystac.extensions.raster import RasterBand, RasterExtension
from pystac.extensions.scientific import ScientificExtension
from pystac.item import Item
from pystac.link import Link
from pystac.summaries import Summaries
from pystac.utils import str_to_datetime
from shapely.geometry import box

from stactools.worldpop.constants import (
    API_URL,
    COLLECTIONS_METADATA,
    KEYWORDS,
    LICENSE,
    PROVIDERS,
    WORLDPOP_EPSG,
    WORLDPOP_EXTENT,
)

logger = logging.getLogger(__name__)


def create_collection(project: str, category: str) -> Collection:
    """Create a STAC Collection WorldPop data.
    Args:
        project (str): WorldPop project ID.
        category (str): WorldPop category ID (member of `project`).
    Returns:
        Collection: STAC Collection object.
    """
    # Check the project and the category exist
    try:
        project_metadata = COLLECTIONS_METADATA[project]
    except KeyError:
        print(f"Project doesn't exist: {project}")
    try:
        category_metadata = project_metadata.get(category)
    except KeyError:
        print(f"Category doesn't exist: {project}/{category}")

    temporal_extent = [
        str_to_datetime(dt) if dt is not None else None
        for dt in category_metadata["time_extent"]
    ]

    extent = Extent(
        SpatialExtent([WORLDPOP_EXTENT]),
        TemporalExtent(temporal_extent),
    )

    collection = Collection(
        id=category_metadata["id"],
        description=category_metadata["description"],
        title=category_metadata["title"],
        license=LICENSE,
        keywords=KEYWORDS,
        providers=PROVIDERS,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
        extent=extent,
        summaries=Summaries({
            "gsd": [category_metadata["gsd"]],
        }),
    )

    # Include projection information
    proj_ext = SummariesProjectionExtension(collection)
    proj_ext.epsg = [WORLDPOP_EPSG]

    # Include scientific information
    scientific = ScientificExtension.ext(collection, add_if_missing=True)
    scientific.doi = category_metadata["doi"]
    scientific.citation = category_metadata["citation"]

    # Include Item Asset information
    item_asset_ext = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_asset_ext.item_assets = {
        "metadata":
        AssetDefinition(
            dict(
                types=[MediaType.JSON],
                roles=["metadata"],
                title="WorldPop Metadata",
            )),
        "thumbnail":
        AssetDefinition(
            dict(
                types=[MediaType.PNG],
                roles=["thumbnail"],
                title="WorldPop Thumbnail",
            )),
        "worldpop":
        AssetDefinition({
            "types": [MediaType.GEOTIFF, "application/zip"],
            "roles": ["data"],
            "title": "WorldPop Data",
            "proj:epsg": WORLDPOP_EPSG
        })
    }

    return collection


def create_item(project: str,
                category: str,
                iso3: str,
                popyear: str,
                metadatas: List[Any],
                cog_hrefs: List[str] = [""],
                tiled: bool = False) -> Union[Item, None]:
    """Returns a STAC Item for a given (project, category, iso3, popyear).

    Args:
        project (str): WorldPop project ID.
        category (str): WorldPop category ID (member of `project`).
        iso3 (str): ISO3 code for a country.
        popyear (str): Population year.
        metadatas (list): List of metadata dicts.
        tif_urls (List[str]): Paths to GeoTIFFs. If "", Item uses original GeoTIFF urls.
    Returns:
        Item: STAC Item object.
    """

    # Get the specific metadata for a popyear
    metadata_popyear = [m for m in metadatas if m["popyear"] == popyear]
    if len(metadata_popyear) == 0:
        print(f"No metadata found for {project}/{category}/{iso3}/{popyear}")
        return None
    metadata = metadata_popyear[0]

    # Use cogs or source tif hrefs
    if cog_hrefs[0] == "":
        tif_hrefs = metadata["files"]
    else:
        tif_hrefs = cog_hrefs
    if tiled:
        tile_id = "_" + "_".join(tif_hrefs[0].split("_")[-3:-1])
    else:
        tile_id = ""

    # Use FTP server because HTTPS server doesn't work with rasterio.open
    with rasterio.open(tif_hrefs[0].replace("https://data",
                                            "ftp://ftp")) as src:
        bbox = src.bounds
        shape = src.shape
        transform = src.transform
        wkt = src.crs.wkt
        epsg = src.meta["crs"].to_epsg()
        nodata = src.nodata
        dtype = src.dtypes[0]

    # Create bbox and geometry
    if epsg != WORLDPOP_EPSG:
        raise AssertionError(
            f"Expecting EPSG={WORLDPOP_EPSG} but got EPSG={epsg} for {project}/{category}"
        )
    polygon = box(*bbox, ccw=True)
    coordinates = [list(i) for i in list(polygon.exterior.coords)]
    geometry = {"type": "Polygon", "coordinates": [coordinates]}

    # Item properties
    properties = {
        "title": metadata["title"],
        "description": metadata["desc"],
        "start_datetime": f"{popyear}-01-01T00:00:00Z",
        "end_datetime": f"{popyear}-12-31T00:00:00Z",
        "gsd": COLLECTIONS_METADATA[project][category]["gsd"],
    }

    # Create item
    item = Item(
        id=f"{iso3}_{popyear}{tile_id}",
        geometry=geometry,
        bbox=bbox,
        datetime=str_to_datetime(f"{popyear}, 1, 1"),
        properties=properties,
    )

    # Create summary link
    item.add_link(
        Link(
            rel="child",
            target=metadata["url_summary"],
            title="Summary Page",
        ))

    # Include thumbnail
    item.add_asset(
        "thumbnail",
        Asset(
            href=metadata["url_img"],
            media_type=MediaType.PNG,
            roles=["thumbnail"],
            title="WorldPop Thumbnail",
        ),
    )

    # Include JSON metadata
    item.add_asset(
        "metadata",
        Asset(
            href=f"{API_URL}/{project}/{category}?iso3={iso3}",
            media_type=MediaType.JSON,
            roles=["metadata"],
            title="WorldPop Metadata",
        ),
    )

    # Incluce scientific information
    sci_ext = ScientificExtension.ext(item, add_if_missing=True)
    sci_ext.doi = metadata["doi"]
    sci_ext.citation = metadata["citation"]

    # Include projection information
    proj_ext = ProjectionExtension.ext(item, add_if_missing=True)
    proj_ext.epsg = epsg
    proj_ext.transform = transform
    proj_ext.bbox = bbox
    proj_ext.wkt2 = wkt
    proj_ext.shape = shape

    # Create data assets
    for tif_href in sorted(tif_hrefs):
        try:
            media_type = {
                "tif":
                MediaType.COG if cog_hrefs[0] != "" else MediaType.GEOTIFF,
                "zip": "application/zip"
            }[tif_href[-3:].lower()]
        except KeyError:
            print(f"Unknown media type for {tif_href}")
        title = os.path.basename(tif_href)[:-4]
        data_asset = Asset(href=tif_href,
                           media_type=media_type,
                           roles=["data"],
                           title=title)

        item.add_asset(title, data_asset)

        # Include raster information
        sampling: Any = "area"
        rast_band = RasterBand.create(nodata=nodata,
                                      data_type=dtype,
                                      sampling=sampling)
        rast_ext = RasterExtension.ext(data_asset, add_if_missing=True)
        rast_ext.bands = [rast_band]

    return item
