import os
import pathlib
import re

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = "Modelling COVID-19 Spread"
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_lat_lon = pd.read_csv(
    os.path.join(APP_PATH, os.path.join("data", "lat_lon_counties.csv"))
)
df_lat_lon["FIPS "] = df_lat_lon["FIPS "].apply(lambda x: str(x).zfill(5))

df_full_data = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("data", "covid_infection_monthly.csv")
    )
)
df_full_data["County Code"] = df_full_data["County Code"].apply(
    lambda x: str(x).zfill(5)
)
# df_full_data["County"] = (
#     df_full_data["Unnamed: 0"] + ", " + df_full_data.County.map(str)
# )
# print(df_full_data)
# df_full_data["County"] = (
#     df_full_data.County.map(str)
# )

MONTHS = ['August', 'September', 'October', 'November', 'December','January', 'February', 'March', 'April', 'May', 'June', 'July']

BINS = [
    "0-2",
    "2.1-4",
    "4.1-6",
    "6.1-8",
    "8.1-10",
    "10.1-12",
    "12.1-14",
    "14.1-16",
    "16.1-18",
    "18.1-20",
    "20.1-22",
    "22.1-24",
    "24.1-26",
    "26.1-28",
    "28.1-30",
    ">30",
]

DEFAULT_COLORSCALE = [
    "#f4e6ff",
    "#eacfff",
    "#e2bdff",
    "#d7a3ff",
    "#cb87ff",
    "#c273ff",
    "#b95eff",
    "#af47ff",
    "#a836ff",
    "#9f21ff",
    "#960dff",
    "#8800f0",
    "#6400b0",
    "#480080",
    "#2e0052",
    "#170029",
]

DEFAULT_OPACITY = 0.8

# mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_access_token = "pk.eyJ1IjoicmF1bmFrcyIsImEiOiJja3dpbXQ1NWowb3Y4Mm9sNTdoNjBreHdqIn0.pEa4wnRKGudDG8E7SzxUGw"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.A(
                    html.Img(id="logo", src=app.get_asset_url("logo-interlocking-uh-red.png")),
                    href="http://www2.cs.uh.edu/~chengu/Teaching/Fall2021/COSC6344_Visualization_Fall2021.html",
                ),
                html.A(
                    html.Button("Raunak Sarbajna", className="link-button"),
                    href="https://github.com/RaunakDune",
                ),
                html.A(
                    html.Button("Source Code", className="link-button"),
                    href="https://github.com/RaunakDune/vis-movement-covid-final",
                ),
                html.H4(children="Modelling the Covid-19 Epidemic"),
                html.P(
                    id="description",
                    children="Using data from SafeGraph to idetify patterns that lead to increased COVID-19 infection.",
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the Month:",
                                ),
                                dcc.Slider(
                                    id="months-slider",
                                    min=0,
                                    max=11,
                                    value=0,
                                    marks={
                                        str(m): {
                                            "label": str(MONTHS[m]),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for m in range(0,12)
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Heatmap of age adjusted mortality rates \
                            from COVID in the month of {0}".format(
                                        MONTHS[0]
                                    ),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=dict(
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=38.72490, lon=-95.61446
                                                ),
                                                pitch=0,
                                                zoom=3.5,
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Histogram of total number of infections (single month)",
                                    "value": "show_absolute_infections_every_month",
                                },
                                {
                                    "label": "Histogram of total number of infections (2020~2021)",
                                    "value": "absolute_infections_all_time",
                                },
                                {
                                    "label": "Age-adjusted infection rate (single month)",
                                    "value": "show_infection_rates_every_month",
                                },
                                {
                                    "label": "Trends in age-adjusted infection rate (2020~2021)",
                                    "value": "infection_rate_all_time",
                                },
                            ],
                            value="show_infection_rates_every_month",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("county-choropleth", "figure"),
    [Input("months-slider", "value")],
    [State("county-choropleth", "figure")],
)
def display_map(month, figure):
    month = MONTHS[month]
    cm = dict(zip(BINS, DEFAULT_COLORSCALE))

    data = [
        dict(
            lat=df_lat_lon["Latitude "],
            lon=df_lat_lon["Longitude"],
            text=df_lat_lon["Hover"],
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0),
        )
    ]

    annotations = [
        dict(
            showarrow=False,
            align="right",
            text="<b>Age-adjusted infection rate<br>per county per month</b>",
            font=dict(color="#2cfec1"),
            bgcolor="#1f2630",
            x=0.95,
            y=0.95,
        )
    ]

    for i, bin in enumerate(reversed(BINS)):
        color = cm[bin]
        annotations.append(
            dict(
                arrowcolor=color,
                text=bin,
                x=0.95,
                y=0.85 - (i / 20),
                ax=-60,
                ay=0,
                arrowwidth=5,
                arrowhead=0,
                bgcolor="#1f2630",
                font=dict(color="#2cfec1"),
            )
        )

    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = 38.72490
        lon = -95.61446
        zoom = 3.5

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            style=mapbox_style,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso",
    )

    base_url = "https://raw.githubusercontent.com/jackparmer/mapbox-counties/master/"
    loc = MONTHS.index(month)+2004
    for bin in BINS:
        geo_layer = dict(
            sourcetype="geojson",
            source=base_url + str(loc) + "/" + bin + ".geojson",
            type="fill",
            color=cm[bin],
            opacity=DEFAULT_OPACITY,
            fill=dict(outlinecolor="#afafaf"),
        )
        layout["mapbox"]["layers"].append(geo_layer)

    fig = dict(data=data, layout=layout)
    return fig


@app.callback(Output("heatmap-title", "children"), [Input("months-slider", "value")])
def update_map_title(month):
    return "Heatmap of age adjusted infection rates \
				from COVID in the month of {0}".format(
        MONTHS[month]
    )


@app.callback(
    Output("selected-data", "figure"),
    [
        Input("county-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("months-slider", "value"),
    ],
)
def display_selected_data(selectedData, chart_dropdown, month):
    month = MONTHS[month]
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Click-drag on the map to select counties",
                paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )
    pts = selectedData["points"]
    fips = [str(pt["text"].split("<br>")[-1]) for pt in pts]
    for i in range(len(fips)):
        if len(fips[i]) == 4:
            fips[i] = "0" + fips[i]
    dff = df_full_data[df_full_data["County Code"].isin(fips)]
    dff = dff.sort_values("Month")
    print(dff)

    regex_pat = re.compile(r"Unreliable", flags=re.IGNORECASE)
    dff["Age Adjusted Rate"] = dff["Age Adjusted Rate"].replace(regex_pat, 0)

    if chart_dropdown != "infection_rate_all_time":
        title = "Absolute infection per county, <b>1999-2016</b>"
        AGGREGATE_BY = "Infection"
        if "show_absolute_infections_every_month" == chart_dropdown:
            dff = dff[dff.Month == month]
            title = "Absolute infection per county, <b>{0}</b>".format(month)
        elif "show_infection_rates_every_month" == chart_dropdown:
            dff = dff[dff.Month == month]
            title = "Age-adjusted infection rate per county, <b>{0}</b>".format(month)
            AGGREGATE_BY = "Age Adjusted Rate"

        dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
        infection_rate_by_fips = dff.groupby("County")[AGGREGATE_BY].sum()
        infection_rate_by_fips = infection_rate_by_fips.sort_values()
        # Only look at non-zero rows:
        infection_rate_by_fips = infection_rate_by_fips[infection_rate_by_fips > 0]
        fig = infection_rate_by_fips.iplot(
            kind="bar", y=AGGREGATE_BY, title=title, asFigure=True
        )

        fig_layout = fig["layout"]
        fig_data = fig["data"]

        fig_data[0]["text"] = infection_rate_by_fips.values.tolist()
        fig_data[0]["marker"]["color"] = "#2cfec1"
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#1f2630"
        fig_layout["plot_bgcolor"] = "#1f2630"
        fig_layout["font"]["color"] = "#2cfec1"
        fig_layout["title"]["font"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["yaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["margin"]["t"] = 75
        fig_layout["margin"]["r"] = 50
        fig_layout["margin"]["b"] = 100
        fig_layout["margin"]["l"] = 50

        return fig

    fig = dff.iplot(
        kind="area",
        x="Month",
        y="Age Adjusted Rate",
        text="County",
        categories="County",
        colors=[
            "#1b9e77",
            "#d95f02",
            "#7570b3",
            "#e7298a",
            "#66a61e",
            "#e6ab02",
            "#a6761d",
            "#666666",
            "#1b9e77",
        ],
        vline=[month],
        asFigure=True,
    )

    for i, trace in enumerate(fig["data"]):
        trace["mode"] = "lines+markers"
        trace["marker"]["size"] = 4
        trace["marker"]["line"]["width"] = 1
        trace["type"] = "scatter"
        for prop in trace:
            fig["data"][i][prop] = trace[prop]

    # Only show first 500 lines
    fig["data"] = fig["data"][0:500]

    fig_layout = fig["layout"]

    # See plot.ly/python/reference
    fig_layout["yaxis"]["title"] = "Age-adjusted infection rate per county per month"
    fig_layout["xaxis"]["title"] = ""
    fig_layout["yaxis"]["fixedrange"] = True
    fig_layout["xaxis"]["fixedrange"] = False
    fig_layout["hovermode"] = "closest"
    fig_layout["title"] = "<b>{0}</b> counties selected".format(len(fips))
    fig_layout["legend"] = dict(orientation="v")
    fig_layout["autosize"] = True
    fig_layout["paper_bgcolor"] = "#1f2630"
    fig_layout["plot_bgcolor"] = "#1f2630"
    fig_layout["font"]["color"] = "#2cfec1"
    fig_layout["xaxis"]["tickfont"]["color"] = "#2cfec1"
    fig_layout["yaxis"]["tickfont"]["color"] = "#2cfec1"
    fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"

    if len(fips) > 500:
        fig["layout"][
            "title"
        ] = "Age-adjusted infection rate per county per month <br>(only 1st 500 shown)"

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
