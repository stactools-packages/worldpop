# flake8: noqa

from pyproj import CRS
from pystac import Link, Provider, ProviderRole

# TODO
WORLDPOP_ID = "worldpop"
WORLDPOP_EPSG = 4326
WORLDPOP_CRS = CRS.from_epsg(WORLDPOP_EPSG)
WORLDPOP_EXTENT = [-180., 90., 180., -90.]
WORLDPOP_TITLE = "WorldPop Country Datasets"
LICENSE = "CC-BY-4.0"
LICENSE_LINK = Link(
    rel="license",
    target="https://www.worldpop.org/data/licence.txt",
    title="Attribution 4.0 International (CC BY 4.0)",
)

WORLDPOP_DESCRIPTION = """WorldPop was initiated in October 2013 to combine the AfriPop, AsiaPop and AmeriPop population mapping projects. It aims to provide an open access archive of spatial demographic datasets for Central and South America, Africa and Asia to support development, disaster response and health applications."""

PROVIDERS = [
    Provider(
        name="WorldPop",
        roles=[
        ProviderRole.HOST,
        ProviderRole.LICENSOR,
        ProviderRole.PROCESSOR,
        ProviderRole.PRODUCER,
    ],
    url="https://www.worldpop.org/"
    ),
    Provider(
        name="Bill and Melinda Gates Foundation",
        url="http://www.gatesfoundation.org/"
    ),
    Provider(
        name="USAID",
        url="https://www.usaid.gov/"
    ),
    Provider(
        name="UN Foundation",
        url="http://www.unfoundation.org/"
    )
]

KEYWORDS = [
    "Population dynamics",
    "Population distributions",
    "Low income countries",
    "Middle income countries",
    "Spatial demographics",
    "Age and sex structures",
    "Population count",
    "Population",
    "Demographics",
    "Geographical maps",
]

API_URL = "https://www.worldpop.org/rest/data"

DESCRIPTION_POP = """<b>WorldPop produces different types of gridded population count datasets, depending on the methods used and end application. \r\nPlease make sure you have read our <a href=\"/methods/populations\" target=\"_blank\">Mapping Populations</a> overview page before choosing and downloading a dataset.</b> \r\n<br/><br/>   \r\nBespoke methods used to produce datasets for specific individual countries are available through the <b>WorldPop Open Population Repository (WOPR)</b> link below. \r\nThese are 100m resolution gridded population estimates using customized methods (\"<a href=\"https://www.worldpop.org/methods/populations\" target=\"_blank\">bottom-up</a>\" and/or \"<a href=\"https://www.worldpop.org/methods/populations\" target=\"_blank\">top-down</a>\") developed for the latest data available from each country. \r\nThey can also be visualised and explored through the <a href=\"https://apps.worldpop.org/woprVision/\" target=\"_blank\">woprVision App</a>.\r\n<br/>\r\nThe remaining datasets in the links below are produced using the \"<a href=\"/methods/populations\" target=\"_blank\">top-down</a>\" method, \r\nwith either the unconstrained or constrained top-down disaggregation method used. \r\nPlease make sure you read the <a href=\"/methods/top_down_constrained_vs_unconstrained\" target=\"_blank\">Top-down estimation modelling overview page</a> to decide on which datasets best meet your needs. \r\nDatasets are available to download in Geotiff and ASCII XYZ format at a <u>resolution of 3 and 30 arc-seconds (approximately 100m and 1km at the equator, respectively)</u>:\r\n<br/><br/>\r\n- Unconstrained individual countries 2000-2020  ( 1km resolution ): Consistent 1km resolution population count datasets created using \r\n<a href=\"/methods/top_down_constrained_vs_unconstrained\" target=\"_blank\">unconstrained top-down methods</a> for all countries of the World for each year 2000-2020. \r\n<br/>\r\n- Unconstrained individual countries 2000-2020 ( 100m resolution ): Consistent 100m resolution population count datasets created using \r\n<a href=\"/methods/top_down_constrained_vs_unconstrained\" target=\"_blank\">unconstrained top-down methods</a> for all countries of the World for each year 2000-2020. \r\n<br/>\r\n- Unconstrained individual countries 2000-2020 UN adjusted ( 100m resolution ): Consistent 100m resolution population count datasets created using \r\n<a href=\"/methods/top_down_constrained_vs_unconstrained\" target=\"_blank\">unconstrained top-down methods</a> for all countries of the World for each year 2000-2020 and adjusted to match United Nations national population estimates (<a href=\"https://population.un.org/wpp/Download/Files/1_Indicators (Standard)/EXCEL_FILES/1_Population/WPP2019_POP_F01_1_TOTAL_POPULATION_BOTH_SEXES.xlsx\" target=\"_blank\">UN 2019</a>)\r\n<br/>\r\n-Unconstrained individual countries 2000-2020 UN adjusted ( 1km resolution ): Consistent 1km resolution population count datasets created using \r\n<a href=\"/methods/top_down_constrained_vs_unconstrained\" target=\"_blank\">unconstrained top-down methods</a> for all countries of the World for each year 2000-2020 and adjusted to match United Nations national population estimates (<a href=\"https://population.un.org/wpp/Download/Files/1_Indicators (Standard)/EXCEL_FILES/1_Population/WPP2019_POP_F01_1_TOTAL_POPULATION_BOTH_SEXES.xlsx\" target=\"_blank\">UN 2019</a>).\r\n<br/>\r\n-Unconstrained global mosaics 2000-2020 ( 1km resolution ): Mosaiced 1km resolution versions of the \"Unconstrained individual countries 2000-2020\" datasets.\r\n<br/>\r\n-Constrained individual countries 2020 ( 100m resolution ): Consistent 100m resolution population count datasets created using \r\n<a href=\"/methods/top_down_constrained_vs_unconstrained\" target=\"_blank\">constrained top-down methods</a> for all countries of the World for 2020.\r\n<br/>\r\n-Constrained individual countries 2020 UN adjusted ( 100m resolution ): Consistent 100m resolution population count datasets created using \r\n<a href=\"/methods/top_down_constrained_vs_unconstrained\" target=\"_blank\">constrained top-down methods</a> for all countries of the World for 2020 and adjusted to match United Nations national \r\npopulation estimates (<a href=\"https://population.un.org/wpp/Download/Files/1_Indicators (Standard)/EXCEL_FILES/1_Population/WPP2019_POP_F01_1_TOTAL_POPULATION_BOTH_SEXES.xlsx\" target=\"_blank\">UN 2019</a>).\r\n<br/>\r\n<br/>\r\nOlder datasets produced for specific individual countries and continents, using a set of tailored geospatial inputs and differing \"top-down\" methods and time periods are still available for download here: <a href=\"https://www.worldpop.org/geodata/listing?id=16\">Individual countries</a> and <a href=\"https://www.worldpop.org/geodata/listing?id=17\">Whole Continent</a>.\r\n"""
DESCRIPTION_AGE_SEX = """<b>WorldPop produces different types of gridded population count datasets, depending on the methods used and end application. \r\nPlease make sure you have read our <a href=\"/methods/populations\" target=\"_blank\">Mapping Populations</a> overview page before choosing and downloading a dataset.</b> \r\n<br/><br/>   \r\n\r\nA description of the modelling methods used for age and sex structures can be found in \r\n<a href=\"https://pophealthmetrics.biomedcentral.com/articles/10.1186/1478-7954-11-11\" target=\"_blank\">\r\nTatem et al</a> and \r\n<a href=\"https://dx.doi.org/10.1038/sdata.2017.89\" target=\"_blank\">Pezzulo et al</a>. Details of the input population count datasets used can be found <a href=\"https://www.worldpop.org/project/categories?id=3\" target=\"_blank\">here</a>, and age/sex structure proportion datasets <a href=\"https://www.portal.worldpop.org/demographics/data/global_agesex_proportions_totals_2020.zip\" target=\"_blank\">here</a>. \r\n<br/>\r\nBoth top-down 'unconstrained' and 'constrained' versions of the datasets are available, and the differences between the two methods are outlined \r\n<a href=\"/methods/top_down_constrained_vs_unconstrained\" target=\"_blank\">here</a>. The  datasets represent the outputs from a project focused on construction of consistent 100m resolution population count datasets for all countries of the World structured by male/female and 5-year age classes (plus a <1 year class). These efforts necessarily involved some shortcuts for consistency. The unconstrained datasets are available for each year from 2000 to 2020.  \r\nThe constrained datasets are only available for 2020 at present, given the time periods represented by the building footprint and built settlement datasets used in the mapping."""
TIME_EXTENT_2020 = ["2020-01-01T00:00:00Z", "2020-12-31T00:00:00Z"]
TIME_EXTENT_2000_ = ["2000-01-01T00:00:00Z", None]

COLLECTIONS_METADATA = {
    "pop": {
        "wpgpunadj": {
            "id": "pop_wpgpunadj",
            "title": """Population counts, unconstrained individual countries 2000-2020 UN adjusted (100m resolution)""",
            "description": DESCRIPTION_POP,
            "time_extent": TIME_EXTENT_2000_,
            "gsd": 100.,
            "doi": "10.5258/SOTON/WP00660",
            "citation": """WorldPop (www.worldpop.org - School of Geography and Environmental Science, University of Southampton; Department of Geography and Geosciences, University of Louisville; Departement de Geographie, Universite de Namur) and Center for International Earth Science Information Network (CIESIN), Columbia University (2018). Global High Resolution Population Denominators Project - Funded by The Bill and Melinda Gates Foundation (OPP1134076). https://dx.doi.org/10.5258/SOTON/WP00660"""
        }, 
        "cic2020_UNadj_100m": {
            "id": "pop_cic2020_UNadj_100m",
            "title": """Population counts, constrained Individual countries 2020 UN adjusted (100m resolution)""",
            "description": DESCRIPTION_POP,
            "time_extent": TIME_EXTENT_2020,
            "gsd": 100.,
            "doi": "10.5258/SOTON/WP00685",
            "citation": """Bondarenko M., Kerr D., Sorichetta A., and Tatem, A.J. 2020. Census/projection-disaggregated gridded population datasets, adjusted to match the corresponding UNPD 2020 estimates, for 183 countries in 2020 using Built-Settlement Growth Model (BSGM) outputs. WorldPop, University of Southampton, UK. doi:10.5258/SOTON/WP00685"""
        }, 
        }, 
    "age_structures": {
        "aswpgp": {
            "id": "age_structures_aswpgp",
            "title": """Age and sex structures, unconstrained individual countries 2000-2020 (100m resolution)""",
            "description": DESCRIPTION_AGE_SEX,
            "time_extent": TIME_EXTENT_2000_,
            "gsd": 100.,
            "doi": "10.5258/SOTON/WP00646",
            "citation": """WorldPop (www.worldpop.org - School of Geography and Environmental Science, University of Southampton; Department of Geography and Geosciences, University of Louisville; Departement de Geographie, Universite de Namur) and Center for International Earth Science Information Network (CIESIN), Columbia University (2018). Global High Resolution Population Denominators Project - Funded by The Bill and Melinda Gates Foundation (OPP1134076). https://dx.doi.org/10.5258/SOTON/WP00646"""
        }, 
        "ascicua_2020": {
            "id": "age_structures_ascicua_2020",
            "title": """Age and sex structures, constrained individual countries 2020 UN adjusted (100m resolution)""",
            "description": DESCRIPTION_AGE_SEX,
            "time_extent": TIME_EXTENT_2020,
            "gsd": 100.,
            "doi": "10.5258/SOTON/WP00698",
            "citation": """Bondarenko M., Kerr D., Sorichetta A., and Tatem, A.J. 2020. Estimates of 2020 total number of people per grid square, adjusted to match the corresponding UNPD 2020 estimates and broken down by gender and age groupings, produced using Built-Settlement Growth Model (BSGM) outputs. WorldPop, University of Southampton, UK. doi:10.5258/SOTON/WP00698"""
        }, 
        }
    }