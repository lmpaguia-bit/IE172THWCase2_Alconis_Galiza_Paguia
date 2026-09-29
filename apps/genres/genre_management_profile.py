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


# =========================================================
# CHANGE SUBMIT BUTTON IF DELETE IS CHECKED
# =========================================================

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


# =========================================================
# DETERMINE ADD MODE OR EDIT MODE
# =========================================================

@app.callback(
    [
        Output('genreprofile_genreid', 'data'),
        Output('genreprofile_deletediv', 'className')
    ],
    [
        Input('url', 'pathname'),
        Input('url', 'search')
    ]
)
def genreprofile_initialize(pathname, urlsearch):

    if pathname != '/genres/genre_management_profile':
        raise PreventUpdate

    parsed = urlparse(urlsearch or '')
    query_dict = parse_qs(parsed.query)

    create_mode = query_dict.get('mode', ['add'])[0]

    # ADD MODE
    if create_mode == 'add':
        genreid = 0
        deletediv = 'd-none'

    # EDIT MODE
    else:
        genreid = int(
            query_dict.get('id', [0])[0]
        )

        deletediv = ''

    return genreid, deletediv


# =========================================================
# SAVE / UPDATE / DELETE GENRE
# =========================================================

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

    # Make sure Submit button actually triggered callback
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

    # Get mode from URL
    parsed = urlparse(urlsearch or '')

    create_mode = parse_qs(
        parsed.query
    ).get(
        'mode',
        ['add']
    )[0]

    # Modal header
    if create_mode == 'add':
        modal_header_text = 'Save Success'

    else:
        modal_header_text = 'Update Success'


    # =====================================================
    # DELETE
    # =====================================================

    if deleteind and 1 in deleteind:

        sql = """
            UPDATE genres
            SET genre_delete_ind = True
            WHERE genre_id = %s
        """

        modifyDB(
            sql,
            [genreid]
        )

        modal_open = True
        modal_header_text = 'Delete Success'

        return [
            alert_color,
            alert_text,
            alert_open,
            modal_open,
            modal_header_text
        ]


    # =====================================================
    # VALIDATION - EMPTY GENRE
    # =====================================================

    if not genre_name:

        alert_open = True
        alert_color = 'danger'

        alert_text = (
            'Check your inputs. '
            'Please supply the genre name.'
        )


    # =====================================================
    # ADD MODE
    # =====================================================

    elif create_mode == 'add':

        # Check if genre already exists
        sql = """
            SELECT genre_id
            FROM genres
            WHERE LOWER(genre_name) = LOWER(%s)
            AND NOT genre_delete_ind
        """

        df = getDataFromDB(
            sql,
            [genre_name],
            ['genreid']
        )

        # Duplicate genre found
        if not df.empty:

            alert_open = True
            alert_color = 'danger'

            alert_text = (
                'Genre already exists. '
                'Please enter a different genre name.'
            )

        # No duplicate -> insert genre
        else:

            sql = """
                INSERT INTO genres
                    (
                        genre_name,
                        genre_delete_ind
                    )
                VALUES (%s, %s)
            """

            modifyDB(
                sql,
                [
                    genre_name,
                    False
                ]
            )

            modal_open = True


    # =====================================================
    # EDIT MODE
    # =====================================================

    else:

        sql = """
            UPDATE genres
            SET genre_name = %s
            WHERE genre_id = %s
        """

        modifyDB(
            sql,
            [
                genre_name,
                genreid
            ]
        )

        modal_open = True


    return [
        alert_color,
        alert_text,
        alert_open,
        modal_open,
        modal_header_text
    ]


# =========================================================
# LOAD EXISTING GENRE IN EDIT MODE
# =========================================================

@app.callback(
    Output('genreprofile_name', 'value'),
    Input('genreprofile_genreid', 'data')
)
def genreprofile_loadprofile(genreid):

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
            return df['genrename'].iloc[0]

    raise PreventUpdate