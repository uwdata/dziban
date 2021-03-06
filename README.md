# Dziban

WIP

## Prototype Status

Current prototype: MKIV.

## Tutorial & Demo

Check out the [Notebook](https://github.com/haldenl/dziban/blob/master/examples/MKIV.ipynb).

Here's a quick peek.

![img](https://github.com/haldenl/dziban/blob/master/examples/example.png)

## Installation

1. Clone the `multi-vis` branch of `draco`, found [here](https://github.com/uwdata/draco/tree/multi-vis). And follow the installation instructions.

2. Install dependencies: `pip install -r requirements.txt`.

3. Install Dziban: `pip install -e .`.

4. Start up a notebook: `jupyter notebook`.

5. Import Dziban and perhaps a dataset from `vega_datasets`.

```
from dziban.mkiv import Chart
from vega_datasets import data
```

Follow the demo for usage examples.


## The important stuff

`base.py` [<>](https://github.com/haldenl/dziban/blob/master/dziban/mkiv/base.py)
>base definition for a chart, including initialization

`chart.py` [<>](https://github.com/haldenl/dziban/blob/master/dziban/mkiv/chart.py)
>programming layer, exposed to user

`encoding.py` [<>](https://github.com/haldenl/dziban/blob/master/dziban/mkiv/encoding.py)
>AST node for encoding objects

`field.py` [<>](https://github.com/haldenl/dziban/blob/master/dziban/mkiv/field.py)
>field methods for a chart, exposed to user

`graphscape2asp.js` [<>](https://github.com/haldenl/dziban/blob/master/dziban/asp/graphscapeToAsp.js)
>script for translating Graphscape definitions and weights into ASP (to be placed into Draco). See below.

In addition, Dziban uses a modified version of Draco, which supports multi-view and Graphscape's transition reasoning.
This can be found on [this branch](https://github.com/uwdata/draco/tree/multi-vis). There are changes to the original Draco scattered about. Noteably:

`compare.lp` [<>](https://github.com/uwdata/draco/blob/multi-vis/asp/compare.lp)
>transition definitions for Graphscape

`compare_weights.lp` [<>](https://github.com/uwdata/draco/blob/multi-vis/asp/compare_weights.lp)
>weights for these transitions

`The whole system`
>has been modified to allow for multiview reasoning (many other files, e.g. `define.lp`, `soft.lp`, `optimize.lp`, `run.py`, `asp2vl`, `optimize_draco.lp`, `optimize_graphscape.lp`, and more and more).
