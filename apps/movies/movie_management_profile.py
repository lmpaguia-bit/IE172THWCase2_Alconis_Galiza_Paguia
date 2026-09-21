import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, ctx  #NEW: added ctx for modern callback context tracking
from dash.exceptions import PreventUpdate
from urllib.parse import urlparse, parse_qs

from app import app
from apps.dbconnect import getDataFromDB, modifyDB

layout = html.Div(
    [
        dcc.Store(id='movieprofile_movieid', storage_type='memory', data=0),
        
        html.H2('Movie Details'),
        html.Hr(),
        
        dbc.Alert(id='movieprofile_alert', is_open=False),
        
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Title", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text', 
                                id='movieprofile_title',
                                placeholder="Title"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Genre", width=1),
                        dbc.Col(
                            html.Div(
                                dcc.Dropdown(
                                    id='movieprofile_genre',
                                    placeholder='Genre'
                                ),
                                className='dash-bootstrap'
                            ),
                            width=5,
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Release Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='movieprofile_releasedate',
                                placeholder='Release Date',
                                month_format='MMM Do, YY',
                                date=None  #NEW: initialized date to None to prevent initial string mismatch
                            ),
                            width=5, 
                            className='dash-bootstrap'
                        )
                    ],
                    className='mb-3'
                ),
            ]
        ),

        html.Div(
            [
                dbc.Checklist(
                    id='movieprofile_deleteind',
                    options=[dict(value=1, label="Mark as Deleted")],
                    value=[] 
                )
            ], 
            id='movieprofile_deletediv'
        ),

        dbc.Button(
            'Submit',
            id='movieprofile_submit',
            color='primary',
            n_clicks=0
        ),

        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4('Save Success', id='movieprofile_modalheader')  #NEW: added id to dynamically update header text
                ),
                dbc.ModalBody(
                    'Movie record has been successfully updated.'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/movies/movie_management'
                    )
                )
            ],
            centered=True,
            id='movieprofile_successmodal',
            backdrop='static'
        )
    ]
)

# Callback to dynamic button styling
@app.callback(
    [
        Output('movieprofile_submit', 'color'),
        Output('movieprofile_submit', 'children'),
    ],
    [
        Input('movieprofile_deleteind', 'value')
    ]
)
def update_submit_button(delete_val):
    if delete_val and 1 in delete_val:
        return 'danger', 'Delete Record'  #NEW: changes button to red delete action
    return 'primary', 'Submit'  #NEW: resets button to standard submit state


@app.callback(
    [
        Output('movieprofile_genre', 'options'),
        Output('movieprofile_movieid', 'data'),
        Output('movieprofile_deletediv', 'className')        
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search'),
    ]
)
def movieprofile_populategenres(pathname, urlsearch):
    if pathname == '/movies/movie_management_profile':
        sql = """
        SELECT genre_name as label, genre_id as value
        FROM genres 
        WHERE genre_delete_ind = False
        """
        df = getDataFromDB(sql, [], ['label', 'value'])
        genre_options = df.to_dict('records') if not df.empty else []  #NEW: safety check for empty dataframe

        parsed = urlparse(urlsearch or '')  #NEW: handle empty/None search queries safely
        query_dict = parse_qs(parsed.query)  #NEW: parse query params into a dictionary
        create_mode = query_dict.get('mode', ['add'])[0]  #NEW: retrieve create mode safely
        
        if create_mode == 'add':
            movieid = 0
            deletediv = 'd-none'
        else:
            movieid = int(query_dict.get('id', [0])[0])  #NEW: get movie ID safely from query params
            deletediv = ''
        
        return [genre_options, movieid, deletediv]

    raise PreventUpdate


# Save / Update / Delete Callback
@app.callback(
    [
        Output('movieprofile_alert', 'color'),
        Output('movieprofile_alert', 'children'),
        Output('movieprofile_alert', 'is_open'),
        Output('movieprofile_successmodal', 'is_open'),
        Output('movieprofile_modalheader', 'children'),  #NEW: output target for dynamic modal title
    ],
    [
        Input('movieprofile_submit', 'n_clicks')
    ],
    [
        State('movieprofile_title', 'value'),
        State('movieprofile_genre', 'value'),
        State('movieprofile_releasedate', 'date'),
        State('url', 'search'),
        State('movieprofile_movieid', 'data'),
        State('movieprofile_deleteind', 'value'),  #NEW: added state to read checkbox selection
    ],
    prevent_initial_call=True  #NEW: prevents callback from running automatically on page load to eliminate duplicate rows
)
def movieprofile_saveprofile(submitbtn, title, genre, releasedate, urlsearch, movieid, deleteind):
    # Check if the submit button was actually clicked
    if not ctx.triggered_id or ctx.triggered_id != 'movieprofile_submit' or not submitbtn:  #NEW: prevents accidental execution on render
        raise PreventUpdate

    alert_open = False
    modal_open = False
    alert_color = ''
    alert_text = ''

    parsed = urlparse(urlsearch or '')  #NEW: safe URL parsing inside callback
    create_mode = parse_qs(parsed.query).get('mode', ['add'])[0]  #NEW: defines create_mode locally inside function scope
    modal_header_text = 'Save Success' if create_mode == 'add' else 'Update Success'  #NEW: dynamic modal header text

    # Handle Delete action
    if deleteind and 1 in deleteind:  #NEW: check if mark as deleted checkbox is checked
        sql = """
            UPDATE movies
            SET movie_delete_ind = True
            WHERE movie_id = %s
        """
        modifyDB(sql, [movieid])  #NEW: perform soft delete in database
        modal_open = True
        modal_header_text = 'Delete Success'  #NEW: set modal header for deletion
        return [alert_color, alert_text, alert_open, modal_open, modal_header_text]  #NEW: returns matching count of 5 elements

    # Validation Checks
    if not title:
        alert_open = True
        alert_color = 'danger'
        alert_text = 'Check your inputs. Please supply the movie title.'
    elif not genre:
        alert_open = True
        alert_color = 'danger'
        alert_text = 'Check your inputs. Please supply the movie genre.'
    elif not releasedate:
        alert_open = True
        alert_color = 'danger'
        alert_text = 'Check your inputs. Please supply the movie release date.'
    else:
        if create_mode == 'add':
            sql = '''
                INSERT INTO movies (movie_name, genre_id, movie_release_date, movie_delete_ind)
                VALUES (%s, %s, %s, %s)
            '''
            values = [title, genre, releasedate, False]
        else:
            sql = '''
                UPDATE movies 
                SET 
                    movie_name = %s,
                    genre_id = %s,
                    movie_release_date = %s
                WHERE
                    movie_id = %s
            '''
            values = [title, genre, releasedate, movieid]

        modifyDB(sql, values)
        modal_open = True

    return [alert_color, alert_text, alert_open, modal_open, modal_header_text]  #NEW: updated return list to include modal header text


@app.callback(
    [
        Output('movieprofile_title', 'value'),
        Output('movieprofile_genre', 'value'),
        Output('movieprofile_releasedate', 'date'),
    ],
    [
        Input('movieprofile_movieid', 'modified_timestamp')
    ],
    [
        State('movieprofile_movieid', 'data'),
    ]
)
def movieprofile_loadprofile(timestamp, movieid):
    if movieid:
        sql = """
            SELECT movie_name, genre_id, movie_release_date
            FROM movies
            WHERE movie_id = %s
        """
        df = getDataFromDB(sql, [movieid], ['moviename', 'genreid', 'releasedate'])

        if not df.empty:  #NEW: check if record exists before indexing
            moviename = df['moviename'][0]
            genreid = int(df['genreid'][0])
            releasedate = df['releasedate'][0]
            return [moviename, genreid, releasedate]

    raise PreventUpdate