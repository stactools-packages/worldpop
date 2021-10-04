[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stactools-packages/worldpop/main?filepath=docs/installation_and_basic_usage.ipynb)

# stactools-worldpop

- Name: worldpop
- Package: `stactools.worldpop`
- PyPI: https://pypi.org/project/stactools-worldpop/
- Owner: @jamesvrt
- Dataset homepage: https://www.worldpop.org/
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)
  - [scientific](https://github.com/stac-extensions/scientific/)
  - [raster](https://github.com/stac-extensions/raster/)
  - [item-assets](https://github.com/stac-extensions/item-assets/)

## Dataset Structure

WorldPop is a collection of 15 "projects" each containing several "categories" covering
 many demographic products and the supporting data used to derive them. This
 package is limited to two projects and two categories within each, totalling four
 categories:

- Project: **Population counts** (`pop`) [[link](https://www.worldpop.org/project/categories?id=3)]
  - Category: Unconstrained, UN adjusted, 100m (`wpgpunadj`) [[link](https://www.worldpop.org/geodata/listing?id=69)]
  - Category: Constrained, UN adjusted, 100m (`cic2020_UNadj_100m`) [[link](https://www.worldpop.org/geodata/listing?id=79)]
- Project: **Population age and sex structure** (`age_structures`) [[link](https://www.worldpop.org/project/categories?id=8)]
  - Category: Unconstrained, 100m (`wpgpunadj`) [[link](https://www.worldpop.org/geodata/listing?id=30)]
  - Category: Constrained, UN adjusted, 100m (`cic2020_UNadj_100m`) [[link](https://www.worldpop.org/geodata/listing?id=88)]

You can read more about unconstrained vs. constrained methods [here](https://www.worldpop.org/methods/top_down_constrained_vs_unconstrained).

## STAC Structure

The STAC is structured to match the project/category format of WorldPop, resulting in
 four separate STAC Collections. Each item in each Collection covers a country.

- Collection: Age and sex pop. structures (unconstrained, 100m)
    - Items: Countries \* years
         - Assets: Ages \* sexes
- Collection: Age and sex pop. structures (constrained, UN adj., 100m)
    - Items: Countries \* 2020
         - Assets: Ages \* sexes
- Collection: Population counts (unconstrained, UN adj., 100m)
    - Items: Countries \* years
         - Assets: Ages \* sexes
- Collection: Population counts (constrained, UN adj., 100m)
    - Items: Countries \* 2020
         - Assets: Ages \* sexes

## STAC Examples

- [Collection](examples/collection.json)
- [Item](examples/FIN_2020.json)

## Command-line usage

To create one Item:

```bash
$ stac worldpop create-item -d destination
```

To create one Collection (not populated with Items):

```bash
$ stac worldpop create-collection -d destination
```

To create one Collection and populate it with Items:

```bash
$ stac worldpop populate-collection -d destination
```

To create all Collections and populate them with Items:

```bash
$ stac worldpop populate-all-collections -d destination
```

Use `stac worldpop --help` to see all subcommands and options.
