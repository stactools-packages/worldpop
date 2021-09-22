import logging
import os

from pystac.link import Link
from stactools.worldpop.utils import get_metadata
from shapely.geometry import box
import rasterio
from typing import Any, Union

from pystac import (Collection, Asset, Extent, SpatialExtent, TemporalExtent, CatalogType,
                    MediaType)

from pystac.extensions.projection import (SummariesProjectionExtension, ProjectionExtension)
from pystac.extensions.scientific import ScientificExtension
from pystac.extensions.raster import RasterExtension, RasterBand
from pystac.extensions.file import FileExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.item import Item
from pystac.summaries import Summaries
from pystac.utils import str_to_datetime

from stactools.worldpop.constants import (
    API_URL,
    CITATION,
    COLLECTION_ID,
    COLLECTIONS_METADATA,
    DATA_TYPE,
    DATASETS,
    DOI,
    EXTENT,
    FILE_SIZES,
    GSD,
    LICENSE,
    NODATA,
    PERIODS,
    PROVIDERS,
    SPATIAL_EXTENTS,
    GSDS,
    HREFS_ZIP,
    HREF_DIR,
    KEYWORDS,
    PROJECTIONS,
    REGIONS,
    SATELLITES,
    TEMPORAL_EXTENT,
    COLLECTION_LICENSE,
    COLLECTION_TITLE,
    COLLECTION_DESCRIPTION,
    NRCAN_PROVIDER,
    INEGI_PROVIDER,
    CONAFOR_PROVIDER,
    TIME_EXTENT_2000_,
    USGS_PROVIDER,
    CEC_PROVIDER,
    HREFS_METADATA,
    VALUES,
    WORLDPOP_DESCRIPTION,
    WORLDPOP_EPSG,
    WORLDPOP_EXTENT,
)

logger = logging.getLogger(__name__)


def create_collection(project: str, category: str) -> Union[Collection, None]:
    """Create a STAC Collection for North American Land Change Monitoring System
     Data.

    These are cartographic products and are intended to be interpreted at the
     resolution identified.

    Read the original metadata for data caveats.

    Returns:
        Collection: STAC Collection object
    """
    # Check the project and the category exist
    project_metadata = COLLECTIONS_METADATA.get(project)
    assert project_metadata != None, f"Project doesn't exist: {project}"
    category_metadata = project_metadata.get(category)
    assert category_metadata != None, f"Category doesn't exist: {project}/{category}"

    extent = Extent(
        SpatialExtent([WORLDPOP_EXTENT]),
        TemporalExtent(category_metadata["time_extent"]),
    )

    collection = Collection(
        id=category_metadata["id"],
        description=category_metadata["description"],
        title=category_metadata["title"],
        license=LICENSE,
        keywords=KEYWORDS,
        providers=[
            PROVIDERS
        ],
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
            "type":[MediaType.GEOTIFF, "application/zip"],
            "roles": ["data"],
            "title": "WorldPop Data",
            "proj:epsg": WORLDPOP_EPSG
        })
    }

    return collection


def create_item(project: str, category: str, iso3: str, popyear: str) -> Union[Item, None]:
    """Returns a STAC Item for a given (region, GSD, year) if that combination
     exists in the dataset, else None.

    Args:
        reg (str): The Region.
        gsd (str): The GSD [m].
        year (str): The year or difference in years (e.g. "2010-2015").
        source (str): The path to the corresponding COG to be included as an
         asset.
    """

    # Get all relevant metadata, using the first to populate Item properties
    metadata_url = f"{API_URL}/{project}/{category}?iso3={iso3}"
    metadatas = get_metadata(metadata_url).get("data")
    metadata = [m for m in metadatas if m["popyear"] == popyear]
    assert len(metadata) == 1, f"{len(metadata)} metadata found for {project}/{category}/{iso3}/{year}"
    metadata = metadata[0]

    # Get raster metadata
    # Use FTP server because HTTPS server doesn't work with rasterio.open
    tif_url = metadata["files"][0].replace("https://data", "ftp://ftp")
    with rasterio.open(tif_url) as src:
        bbox = src.bounds
        shape = src.shape
        transform = src.transform
        wkt = src.crs.wkt
        epsg = src.crs.epsg
        nodata = src.nodata
        dtype = src.dtypes[0]

    # Create bbox and geometry
    assert epsg == WORLDPOP_EPSG, f"Expecting EPSG={WORLDPOP_EPSG} but got EPSG={epsg} for {project}/{category}"
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
        id=f"{iso3}_{popyear}",
        geometry=geometry,
        bbox=bbox,
        datetime=str_to_datetime(f"{popyear}, 1, 1"),
        properties=properties,
    )

    # Create summary link
    item.add_link(Link(
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
            href=metadata_url,
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

    # Include raster information (assume the same for all data assets)
    rast_band = RasterBand.create(
        nodata=nodata,
        sampling="area",
        data_type=dtype
        )
    rast_ext = RasterExtension.ext(item, add_if_missing=True)
    rast_ext.bands = [rast_band]

    # Create data assets
    for href in metadata["files"]:
        media_type = {
            "tif": MediaType.GEOTIFF,
            "zip": "application/zip"
        }.get(href[-3:].lower())
        assert media_type != None, f"Unknown media type for {href}"
        title = os.path.basename(href)[:-4]
        data_asset = Asset(
            href=href,
            media_type=media_type,
            roles=["data"],
            title=title
        )
        item.add_asset(title, data_asset)

    return item