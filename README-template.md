[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stactools-packages/worldpop/main?filepath=docs/installation_and_basic_usage.ipynb)

# stactools-worldpop

- Name: worldpop
- Package: `stactools.worldpop`
- PyPI: https://pypi.org/project/stactools-worldpop/
- Owner: @githubusername
- Dataset homepage: http://example.com
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)
- Extra fields:
  - `worldpop:custom`: A custom attribute

**STAC Structure**:

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

## Examples

### STAC objects

- [Collection](examples/collection.json)
- [Item](examples/item/item.json)

### Command-line usage

Description of the command line functions

```bash
$ stac worldpop create-item source destination
```

Use `stac worldpop --help` to see all subcommands and options.
