import os
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, dash_table
from utils.snowflake_connector import get_snowflake_dfs

DATA_SOURCE = os.getenv("DATA_SOURCE", "local").lower()

app = Dash(__name__, suppress_callback_exceptions=True, title="Multimodal Biological Visualization")
server = app.server

def load_local():
    clinical = pd.read_csv("data/clinical.csv")
    spatial = pd.read_csv("data/spatial_expression.csv")
    genes = pd.read_csv("data/genes.csv")
    return clinical, spatial, genes

if DATA_SOURCE == "snowflake":
    try:
        clinical, spatial, genes = get_snowflake_dfs()
    except Exception as e:
        print("Falling back to local due to Snowflake error:", e)
        clinical, spatial, genes = load_local()
else:
    clinical, spatial, genes = load_local()

gene_options = [{"label": g, "value": g} for g in sorted(genes["gene_symbol"].unique())]
diagnosis_options = [{"label": d, "value": d} for d in sorted(clinical["diagnosis"].unique())]

app.layout = html.Div([
    html.H1("Multimodal Biological Visualization Platform"),
    html.Div("Explore spatial transcriptomics alongside clinical features to generate hypotheses."),
    html.Div([
        html.Div([html.Label("Select Gene"),
                  dcc.Dropdown(id="gene", options=gene_options, value=gene_options[0]["value"], clearable=False)], 
                 style={"flex":1,"minWidth":280}),
        html.Div([html.Label("Filter by Diagnosis"),
                  dcc.Dropdown(id="dx", options=[{"label":"All","value":"__all__"}]+diagnosis_options, value="__all__", clearable=False)],
                 style={"flex":1,"minWidth":280}),
        html.Div([html.Label("Min Expression"),
                  dcc.Slider(id="min_expr", min=0, max=10, step=0.1, value=0.5,
                             tooltip={"placement":"bottom","always_visible":True})],
                 style={"flex":1,"minWidth":280,"padding":"0 12px"}),
    ], style={"display":"flex","gap":"16px","flexWrap":"wrap","margin":"16px 0"}),
    dcc.Tabs(value="tab-spatial", children=[
        dcc.Tab(label="Spatial Map", value="tab-spatial", children=[dcc.Loading(dcc.Graph(id="spatial-map"))]),
        dcc.Tab(label="Expression vs Clinical", value="tab-scatter", children=[
            html.Div([html.Label("Clinical Feature"),
                      dcc.Dropdown(id="clinical-feature", options=[{"label":c,"value":c} for c in ["age","tumor_stage_numeric","survival_months"]], value="age")],
                     style={"width":300,"margin":"12px 0"}),
            dcc.Loading(dcc.Graph(id="expr-vs-clinical"))
        ]),
        dcc.Tab(label="Table View", value="tab-table", children=[
            dash_table.DataTable(
                id="table",
                page_size=10,
                filter_action="native",
                sort_action="native",
                style_table={"overflowX":"auto"},
                columns=[{"name":c,"id":c} for c in ["spot_id","sample_id","x","y","gene","expr","diagnosis","age","tumor_stage_numeric","survival_months"]]
            )
        ])
    ]),
    html.Hr(),
    html.Div("Tip: Switch DATA_SOURCE=snowflake and set credentials to query live data.")
], style={"maxWidth":"1200px","margin":"0 auto","padding":"16px"})

@app.callback(Output("spatial-map","figure"), Input("gene","value"), Input("dx","value"), Input("min_expr","value"))
def update_spatial(gene, dx, min_expr):
    df = spatial[spatial["gene"] == gene].merge(clinical, on="sample_id", how="left")
    if dx != "__all__":
        df = df[df["diagnosis"] == dx]
    df = df[df["expr"] >= float(min_expr)]
    if df.empty:
        fig = px.scatter(x=[], y=[], title="No data for current filters")
        fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
        return fig
    fig = px.scatter(df, x="x", y="y", color="expr",
                     hover_data=["sample_id","diagnosis","age","tumor_stage_numeric","survival_months"],
                     title=f"Spatial expression map: {gene}")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(legend_title="Expression")
    return fig

@app.callback(Output("expr-vs-clinical","figure"), Input("gene","value"), Input("clinical-feature","value"), Input("dx","value"))
def update_scatter(gene, clin_feat, dx):
    df = spatial[spatial["gene"] == gene].merge(clinical, on="sample_id", how="left")
    if dx != "__all__":
        df = df[df["diagnosis"] == dx]
    agg = df.groupby("sample_id").agg(expr=("expr","mean"), **{clin_feat:(clin_feat,"mean")}).reset_index()
    if agg.empty:
        return px.scatter(x=[], y=[], title="No data for current filters")
    return px.scatter(agg, x=clin_feat, y="expr", trendline="ols", title=f"{gene} expression vs {clin_feat}")

@app.callback(Output("table","data"), Input("gene","value"), Input("dx","value"), Input("min_expr","value"))
def update_table(gene, dx, min_expr):
    df = spatial[spatial["gene"] == gene].merge(clinical, on="sample_id", how="left")
    if dx != "__all__":
        df = df[df["diagnosis"] == dx]
    return df[df["expr"] >= float(min_expr)][["spot_id","sample_id","x","y","gene","expr","diagnosis","age","tumor_stage_numeric","survival_months"]].to_dict("records")

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.getenv("PORT","8050")), debug=True)
