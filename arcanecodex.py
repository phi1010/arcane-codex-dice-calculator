import marimo

__generated_with = "0.13.14"
app = marimo.App(width="medium", layout_file="layouts/arcanecodex.grid.json")


@app.cell
def _():
    import marimo as mo
    from collections import defaultdict
    import polars as pl
    import altair as al
    return al, defaultdict, mo, pl


@app.cell
def _(defaultdict, mo, pl):
    dice = defaultdict(lambda : 0)
    for x in range(1,10+1):
        for y in range(1,10+1):
            dice[x+y]+=1
    dice = {key:count/sum(dice.values()) for key, count in dice.items()}
    mo.ui.table(pl.DataFrame(iter(dice.items()),orient="row"), pagination=False)
    return (dice,)


@app.cell
def _(dice):
    success = {key:sum((prob for value, prob in dice.items() if value >= key)) for key in range(20)}
    #pl.DataFrame(iter(success.items()),orient="row")
    return


@app.cell
def _(dice):
    def success_with_modifier(key,modifier):
        return sum((prob for value, prob in dice.items() if value+modifier >= key))
    return (success_with_modifier,)


@app.cell
def _(mo):
    modifier = mo.ui.slider(start=0,stop=20)
    mo.md(f"Modifier: {modifier}")
    return (modifier,)


@app.cell
def _(mo, modifier):
    mo.md(rf"""Modifier = {modifier.value}""")
    return


@app.cell
def _(modifier, pl, success_with_modifier):
    #mo.ui.table([{"result":result}|{modifier:success_with_modifier[(result,modifier)] for modifier in range(20)} for result in range(30)],pagination=False)
    df_success_with_modifier = pl.DataFrame({"result":range(0,30)}).with_columns(pl.col("result").map_elements(lambda result: success_with_modifier(result,modifier.value), return_dtype=pl.datatypes.Float64).alias("chance"))
    #mo.ui.table(df_success_with_modifier,pagination=False)
    return (df_success_with_modifier,)


@app.cell
def _(al, df_success_with_modifier, mo, modifier):
    mo.vstack([
        al.Chart(df_success_with_modifier).mark_line().encode(
        x='result',
        y='chance'
        ),
        mo.md(f"modifier = {modifier.value}")
    ])
    return


@app.cell
def _(mo):
    damagedice = mo.ui.slider(start=0,stop=5, value=1)
    damagemodifier = mo.ui.slider(start=0,stop=20)
    minimum = mo.ui.slider(start=0,stop=30, value=15)
    mo.md(f"""
    Damage Dice: {damagedice}

    Damage Modifier: {damagemodifier}

    Minimum Throw: {minimum}
    """)
    return damagedice, damagemodifier, minimum


@app.cell
def _(damagedice, damagemodifier):
    basedamage = (1+10)/2.*damagedice.value + damagemodifier.value
    return (basedamage,)


@app.cell
def _(basedamage, damagedice, damagemodifier, minimum, mo):
    mo.md(
        f"""
    Damage Dice: {damagedice.value}

    Damage Modifier: {damagemodifier.value}

    Base Damage: {basedamage}

    Minimum Throw: {minimum.value}
    """
    )
    return


@app.cell
def _(dice):
    def avg_damage(basedamage,modifier,bidding,minimum):
        return sum((prob for value, prob in dice.items() if value+modifier-bidding >= minimum)) * (basedamage+bidding)
    #avg_damage(5.5*2+7,12,0,20)
    return (avg_damage,)


@app.cell
def _(avg_damage, basedamage, minimum, modifier, pl):
    df_avg_damage = (
        pl.DataFrame({"bidding":range(0,30)})
        .with_columns(
            pl.col("bidding").map_elements(
                lambda bid: avg_damage(basedamage, modifier.value, bid, minimum.value),
                return_dtype=pl.datatypes.Float64)
                .alias("avg damage"))
        )
    return (df_avg_damage,)


@app.cell
def _(
    al,
    basedamage,
    damagedice,
    damagemodifier,
    df_avg_damage,
    minimum,
    mo,
    modifier,
):
    df_avg_damage
    mo.vstack([
    al.Chart(df_avg_damage).mark_line().encode(
        x='bidding',
        y='avg damage'
    ),
    mo.md(f"basedamage = {damagedice.value}W10+{damagemodifier.value} = {basedamage}, modifier = {modifier.value}, enemy minimum = {minimum.value}")
    ])
    return


@app.cell
def _(df_avg_damage, pl):
    df_avg_damage.select(pl.all().sort_by("avg damage").last())
    return


@app.cell
def _(avg_damage, basedamage, modifier, pl):
    def max_damage_bidding(basedamage,modifier,minimum):
        df_avg_damage = pl.DataFrame({"bidding":range(0,30)}).with_columns(pl.col("bidding").map_elements(lambda bid: avg_damage(basedamage, modifier, bid, minimum), return_dtype=pl.datatypes.Float64).alias("avg damage"))
        return df_avg_damage.select(pl.all().sort_by("avg damage").last())["bidding"].item()

    df_max_damage = (
        pl.DataFrame({"minimum":range(0,30)})
        .with_columns(bidding=pl.col("minimum").map_elements(lambda minimum: max_damage_bidding(basedamage, modifier.value, minimum), return_dtype=pl.datatypes.Float64))
        .with_columns(damage=pl.struct('minimum','bidding').map_elements(lambda x: avg_damage(basedamage,modifier.value,x["bidding"],x["minimum"]) , return_dtype=pl.datatypes.Float64))
    )
    return (df_max_damage,)


@app.cell
def _():
    #df_max_damage
    return


@app.cell
def _(al, basedamage, damagedice, damagemodifier, df_max_damage, mo, modifier):

    al.Chart(df_max_damage).mark_line().encode(
        x='minimum',
        y='bidding'
    )

    base = al.Chart(df_max_damage).encode(x='minimum')

    mo.vstack([
        al.layer(
            base.mark_line(color='blue').encode(y='bidding',text='bidding'),
            base.mark_text().encode(y='bidding',text='bidding'),
            base.mark_line(color='red').encode(y='damage',text='damage'),
            base.mark_text().encode(y='damage',text='damage')
        ),
        mo.md(f"basedamage = {damagedice.value}W10+{damagemodifier.value} = {basedamage}, modifier = {modifier.value}")
    ])
    return


@app.cell
def _(avg_damage, basedamage, modifier, pl):
    df_avg_damage_grid = pl.DataFrame([dict(minimum=x,bidding=y) for x in range(0,30) for y in range(0,20)])\
    .with_columns(damage=pl.struct('minimum','bidding').map_elements(lambda x: avg_damage(basedamage,modifier.value,x["bidding"],x["minimum"]) , return_dtype=pl.datatypes.Float64))
    return (df_avg_damage_grid,)


@app.cell
def _():
    #df_avg_damage_grid
    return


@app.cell
def _(
    al,
    basedamage,
    damagedice,
    damagemodifier,
    df_avg_damage_grid,
    mo,
    modifier,
):
    mo.vstack([
        al.Chart(df_avg_damage_grid).mark_rect().encode(
            x='minimum:O',
            y='bidding:O',
            #color='damage:Q',
            color=al.Color('damage:Q').scale(scheme="sinebow")
        ),
        mo.md(f"basedamage = {damagedice.value}W10+{damagemodifier.value} = {basedamage}, modifier = {modifier.value}")
    ])
    return


if __name__ == "__main__":
    app.run()
