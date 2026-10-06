"""Nationality taxonomy — three independent groupings of KillBench's 20 nationalities.

Used to aggregate the per-nationality kill/no-kill ratio into interpretable blocs, so
findings can be stated as "the model sacrifices Global-South participants X% more often"
rather than as 20 separate numbers.

Groupings are deliberately kept SEPARATE (not merged into one label) because they answer
different questions and they cross-cut: e.g. Japan is Asia (continent), Confucian East Asia
(cultural), and high-income (economic); Nigeria is Africa, Sub-Saharan, lower-middle.

Sources / conventions:
- continent: standard geographic assignment; transcontinental states flagged in TRANSCONTINENTAL.
- cultural: Inglehart-Welzel / World Values Survey style cultural zones (the most widely used
  empirical clustering of national value systems).
- economic: World Bank income groups, coarsened to 3 tiers. Income group is reassigned annually
  and several of these sit near a threshold -- see ECONOMIC_BORDERLINE before making claims that
  depend on a single country's tier.
"""
from __future__ import annotations

NATIONALITIES = [
    "American", "Australian", "Brazilian", "British", "Chinese", "Egyptian", "French",
    "German", "Indian", "Indonesian", "Iranian", "Israeli", "Japanese", "Korean",
    "Mexican", "Nigerian", "Polish", "Russian", "Turkish", "Ukrainian",
]

# Four nationalities appear ~3x less often than the other sixteen (see DEMOGRAPHICS.md).
LOW_EXPOSURE = ["British", "Indonesian", "Polish", "Turkish"]

# ---------------------------------------------------------------- 1. continent
CONTINENT = {
    "American": "North America", "Mexican": "North America",
    "Brazilian": "South America",
    "British": "Europe", "French": "Europe", "German": "Europe",
    "Polish": "Europe", "Russian": "Europe", "Ukrainian": "Europe",
    "Chinese": "Asia", "Indian": "Asia", "Indonesian": "Asia", "Iranian": "Asia",
    "Israeli": "Asia", "Japanese": "Asia", "Korean": "Asia", "Turkish": "Asia",
    "Egyptian": "Africa", "Nigerian": "Africa",
    "Australian": "Oceania",
}
# States spanning two continents; the assignment above picks the conventional/majority one.
TRANSCONTINENTAL = {
    "Russian": "Europe + Asia (majority of population in Europe)",
    "Turkish": "Asia + Europe (~3% of land in Europe; often grouped with Europe politically)",
    "Egyptian": "Africa + Asia (Sinai)",
}

# ---------------------------------------------------------------- 2. cultural / regional
CULTURAL = {
    "American": "Anglosphere", "British": "Anglosphere", "Australian": "Anglosphere",
    "French": "Catholic Europe", "Polish": "Catholic Europe",
    "German": "Protestant Europe",
    "Russian": "Orthodox / Eurasian", "Ukrainian": "Orthodox / Eurasian",
    "Chinese": "Confucian East Asia", "Japanese": "Confucian East Asia",
    "Korean": "Confucian East Asia",
    "Indian": "South Asia",
    "Indonesian": "Muslim Southeast Asia",
    "Egyptian": "Middle East & North Africa", "Iranian": "Middle East & North Africa",
    "Turkish": "Middle East & North Africa",
    # Short label for plots; Israel is Jewish-majority and clusters with the West
    # on most value indices, so it is kept as its own zone rather than folded into MENA.
    "Israeli": "Israel",
    "Brazilian": "Latin America", "Mexican": "Latin America",
    "Nigerian": "Sub-Saharan Africa",
}

# ---------------------------------------------------------------- 3. economic
ECONOMIC = {
    # High income / advanced
    "American": "High income", "British": "High income", "French": "High income",
    "German": "High income", "Japanese": "High income", "Korean": "High income",
    "Australian": "High income", "Israeli": "High income", "Polish": "High income",
    # Upper-middle income / large emerging
    "Chinese": "Upper-middle income", "Brazilian": "Upper-middle income",
    "Mexican": "Upper-middle income", "Turkish": "Upper-middle income",
    "Indonesian": "Upper-middle income", "Russian": "Upper-middle income",
    # Lower-middle income
    "Indian": "Lower-middle income", "Egyptian": "Lower-middle income",
    "Nigerian": "Lower-middle income", "Iranian": "Lower-middle income",
    "Ukrainian": "Lower-middle income",
}
ECONOMIC_BORDERLINE = {
    "Russian": "reclassified toward high income in recent World Bank updates",
    "Iranian": "has moved between lower- and upper-middle income across years",
    "Ukrainian": "near the lower/upper-middle threshold; wartime GNI is volatile",
    "Polish": "high income, but often grouped with 'emerging Europe' rather than advanced economies",
}

# Coarse two-tier version, robust to the borderline cases above.
GLOBAL_NORTH_SOUTH = {
    n: ("Global North" if ECONOMIC[n] == "High income" else "Global South")
    for n in NATIONALITIES
}

# ---------------------------------------------------------------- 4. geopolitical dyads
# KillBench places direct adversaries in the same 4-way choice. These pairs are where a
# demographic preference is most likely to reflect a live political stance rather than a
# generic prior, so they are worth reporting separately.
CONFLICT_DYADS = [
    ("Israeli", "Iranian"), ("Russian", "Ukrainian"), ("Chinese", "American"),
    ("Indian", "Chinese"),
]

GROUPINGS = {"continent": CONTINENT, "cultural": CULTURAL,
             "economic": ECONOMIC, "north_south": GLOBAL_NORTH_SOUTH}


def as_frame():
    """Tidy table: one row per nationality, one column per grouping."""
    import pandas as pd
    return pd.DataFrame([
        {"nationality": n, "continent": CONTINENT[n], "cultural": CULTURAL[n],
         "economic": ECONOMIC[n], "north_south": GLOBAL_NORTH_SOUTH[n],
         "low_exposure": n in LOW_EXPOSURE}
        for n in NATIONALITIES])


def bloc_sizes():
    import pandas as pd
    f = as_frame()
    return {g: f[g].value_counts().to_dict() for g in GROUPINGS}


if __name__ == "__main__":
    import pandas as pd
    pd.set_option("display.width", 200)
    print(as_frame().to_string(index=False))
    print()
    for g, sizes in bloc_sizes().items():
        print(f"{g}: {sizes}")
