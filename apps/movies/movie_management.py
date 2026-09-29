import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB

layout = html.Div(
    [
        html.H2('Movies'), # Page Header
        html.Hr(),
        dbc.Card( # Card Container
            [
                dbc.CardHeader( # Define Card Header
                    [
                        html.H3('Manage Records')
                    ]
                ),
                dbc.CardBody( # Define Card Contents
                    [
                        html.Div( # Add Movie Btn
                            [
                                # Add movie button will work like a 
                                # hyperlink that leads to another page
                                dbc.Button(
                                    "Add Movie",
                                    href='/movies/movie_management_profile?mode=add'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            dbc.Form(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Label("Search Title", width=2),
                                            dbc.Col(
                                                dbc.Input(
                                                    type='text',
                                                    id='movie_titlefilter',
                                                    placeholder='Movie Title'
                                                ),
                                                width=5
                                            )
                                        ],
                                        className="mb-2"
                                    ),
                                    # NEW: Checkbox to view deleted records
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Checklist(
                                                    id='movie_include_deleted',
                                                    options=[
                                                        {'label': ' Include deleted entries', 'value': 1}
                                                    ],
                                                    value=[],
                                                ),
                                                width={"size": 5, "offset": 2}
                                            )
                                        ]
                                    )
                                ]
                            )
                        ),

                                html.Div(
                                    "Table with movies will go here.",
                                    id='movie_movielist'
                                )
                            ]
                        )
                    ]
                )
            ]
        )

@app.callback(
    [
        Output('movie_movielist', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('movie_titlefilter', 'value'),
        Input('movie_include_deleted', 'value')  # NEW: Added checkbox input
    ],
)
def updateRecordsTable(pathname, titlefilter, include_deleted):
    if pathname != '/movies/movie_management':
        raise PreventUpdate

    # Base SQL query
    sql = """ 
        SELECT 
            movie_name, 
            genre_name, 
            to_char(movie_release_date, 'DD Mon YYYY'), 
            movie_id,
            movie_delete_ind
        FROM movies m
        INNER JOIN genres g ON m.genre_id = g.genre_id
        WHERE 1=1
    """
    val = []

    # If the checkbox is NOT checked, exclude deleted movies
    if not (include_deleted and 1 in include_deleted):
        sql += " AND NOT movie_delete_ind"

    # Filter by title search term
    if titlefilter:
        sql += " AND movie_name ILIKE %s"
        val += [f'%{titlefilter}%']

    col = ["Movie Title", "Genre", "Release Date", 'id', 'deleted']

    df = getDataFromDB(sql, val, col)

    if df.empty:
        return [html.Div("No records found.", className="text_muted mt-3")]

    # Optional: Highlight or tag deleted items in the table
    df['Action'] = [
        html.Div(
            dbc.Button(
                "Edit", 
                color='warning', 
                size='sm', 
                href=f'/movies/movie_management_profile?mode=edit&id={row["id"]}'
            ),
            className='text-center'
        ) for idx, row in df.iterrows()
    ]

    # Exclude internal columns from table display
    df = df[['Movie Title', 'Genre', 'Release Date', 'Action']]

    movie_table = dbc.Table.from_dataframe(
        df, 
        striped=True, 
        bordered=True,
        hover=True, 
        size='sm'
    )

    return [movie_table]