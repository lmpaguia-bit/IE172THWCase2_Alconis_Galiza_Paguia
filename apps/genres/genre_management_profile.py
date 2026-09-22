import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, ctx
from dash.exceptions import PreventUpdate
from urllib.parse import urlparse, parse_qs

from app import app
from apps.dbconnect import getDataFromDB, modifyDB


layout = html.Div(
    [
        dcc.Store(
            id='genreprofile_genreid',
            storage_type='memory',
            data=0
        ),

        html.H2('Genre Details'),
        html.Hr(),

        dbc.Alert(
            id='genreprofile_alert',
            is_open=False
        ),

        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Genre", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text',
                                id='genreprofile_name',
                                placeholder='Genre Name'
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                )
            ]
        ),

        html.Div(
            [
                dbc.Checklist(
                    id='genreprofile_deleteind',
                    options=[
                        dict(
                            value=1,
                            label='Mark as Deleted'
                        )
                    ],
                    value=[]
                )
            ],
            id='genreprofile_deletediv'
        ),

        dbc.Button(
            'Submit',
            id='genreprofile_submit',
            color='primary',
            n_clicks=0
        ),

        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4(
                        'Save Success',
                        id='genreprofile_modalheader'
                    )
                ),

                dbc.ModalBody(
                    'Genre record has been successfully updated.'
                ),

                dbc.ModalFooter(
                    dbc.Button(
                        'Proceed',
                        href='/genres/genre_management'
                    )
                )
            ],
            centered=True,
            id='genreprofile_successmodal',
            backdrop='static'
        )
    ]
)


# Change Submit button when record is marked for deletion
@app.callback(
    [
        Output('genreprofile_submit', 'color'),
        Output('genreprofile_submit', 'children')
    ],
    [
        Input('genreprofile_deleteind', 'value')
    ]
)
def update_submit_button(delete_val):

    if delete_val and 1 in delete_val:
        return 'danger', 'Delete Record'

    return 'primary', 'Submit'


# Determine whether page is in Add or Edit mode
@app.callback(
    [
        Output('genreprofile_genreid', 'data'),
        Output('genreprofile_deletediv', 'className')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def genreprofile_initialize(pathname, urlsearch):

    if pathname != '/genres/genre_management_profile':
        raise PreventUpdate

    parsed = urlparse(urlsearch or '')
    query_dict = parse_qs(parsed.query)

    create_mode = query_dict.get('mode', ['add'])[0]

    if create_mode == 'add':
        genreid = 0
        deletediv = 'd-none'

    else:
        genreid = int(query_dict.get('id', [0])[0])
        deletediv = ''

    return genreid, deletediv


# Save / Update / Delete Genre
@app.callback(
    [
        Output('genreprofile_alert', 'color'),
        Output('genreprofile_alert', 'children'),
        Output('genreprofile_alert', 'is_open'),
        Output('genreprofile_successmodal', 'is_open'),
        Output('genreprofile_modalheader', 'children')
    ],
    [
        Input('genreprofile_submit', 'n_clicks')
    ],
    [
        State('genreprofile_name', 'value'),
        State('url', 'search'),
        State('genreprofile_genreid', 'data'),
        State('genreprofile_deleteind', 'value')
    ],
    prevent_initial_call=True
)
def genreprofile_saveprofile(
    submitbtn,
    genre_name,
    urlsearch,
    genreid,
    deleteind
):

    if (
        not ctx.triggered_id
        or ctx.triggered_id != 'genreprofile_submit'
        or not submitbtn
    ):
        raise PreventUpdate

    alert_open = False
    modal_open = False
    alert_color = ''
    alert_text = ''

    parsed = urlparse(urlsearch or '')
    create_mode = parse_qs(parsed.query).get(
        'mode',
        ['add']
    )[0]

    modal_header_text = (
        'Save Success'
        if create_mode == 'add'
        else 'Update Success'
    )

    # DELETE
    if deleteind and 1 in deleteind:

        sql = """
            UPDATE genres
            SET genre_delete_ind = True
            WHERE genre_id = %s
        """

        modifyDB(sql, [genreid])

        modal_open = True
        modal_header_text = 'Delete Success'

        return [
            alert_color,
            alert_text,
            alert_open,
            modal_open,
            modal_header_text
        ]

    # VALIDATION
    if not genre_name:

        alert_open = True
        alert_color = 'danger'
        alert_text = (
            'Check your inputs. '
            'Please supply the genre name.'
        )

    # ADD
    elif create_mode == 'add':

        sql = """
            INSERT INTO genres
                (genre_name, genre_delete_ind)
            VALUES (%s, %s)
        """

        modifyDB(
            sql,
            [genre_name, False]
        )

        modal_open = True

    # EDIT
    else:

        sql = """
            UPDATE genres
            SET genre_name = %s
            WHERE genre_id = %s
        """

        modifyDB(
            sql,
            [genre_name, genreid]
        )

        modal_open = True

    return [
        alert_color,
        alert_text,
        alert_open,
        modal_open,
        modal_header_text
    ]


# Load existing genre when in Edit Mode
@app.callback(
    Output('genreprofile_name', 'value'),
    Input('genreprofile_genreid', 'modified_timestamp'),
    State('genreprofile_genreid', 'data')
)
def genreprofile_loadprofile(timestamp, genreid):

    if genreid:

        sql = """
            SELECT genre_name
            FROM genres
            WHERE genre_id = %s
        """

        df = getDataFromDB(
            sql,
            [genreid],
            ['genrename']
        )

        if not df.empty:
            return df['genrename'][0]

    raise PreventUpdate