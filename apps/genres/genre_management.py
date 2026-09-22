import dash_bootstrap_components as dbc
from dash import html, Input, Output
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB


layout = html.Div(
    [
        html.H2('Genres'),
        html.Hr(),

        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Records')
                    ]
                ),

                dbc.CardBody(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Add Genre",
                                    href='/genres/genre_management_profile?mode=add'
                                )
                            ]
                        ),

                        html.Hr(),

                        html.Div(
                            [
                                html.H4('Genre List'),

                                html.Div(
                                    "Table with genres will go here.",
                                    id='genre_genrelist'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


@app.callback(
    Output('genre_genrelist', 'children'),
    Input('url', 'pathname')
)
def updateRecordsTable(pathname):

    if pathname != '/genres/genre_management':
        raise PreventUpdate

    sql = """
        SELECT genre_name, genre_id
        FROM genres
        WHERE NOT genre_delete_ind
        ORDER BY genre_name
    """

    df = getDataFromDB(
        sql,
        [],
        ['Genre', 'id']
    )

    df['Action'] = [
        html.Div(
            dbc.Button(
                "Edit",
                color='warning',
                size='sm',
                href=f'/genres/genre_management_profile?mode=edit&id={row["id"]}'
            ),
            className='text-center'
        )
        for idx, row in df.iterrows()
    ]

    # Do not display genre_id
    df = df[['Genre', 'Action']]

    genre_table = dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        size='sm'
    )

    return genre_table