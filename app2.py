# this version of the app has a upload file

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import io
import base64
import find_significant as fs


samples_sheet = 'SAMPLES'
observations_sheet = 'OBSERVATIONS'

app = dash.Dash()
app.scripts.config.serve_locally = True
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})


app.layout = html.Div([
    html.Div([
        html.H1('Analysis of RPMA Data')
    ]),
        html.Div([
        dcc.Upload(
            html.Button('Upload File'),
            id='upload'
            ),
        html.Div(id='output-data-upload'),
        html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
        html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
        dcc.Graph(id='up-regulated'),
        dcc.Graph(id='down-regulated'),
        html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
        html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
    ])
])


def populate_tables(content_string):
    print('1')
    samples_df = pd.read_excel(io.BytesIO(base64.b64decode(content_string)), sheetname=samples_sheet)
    observations_df = pd.read_excel(io.BytesIO(base64.b64decode(content_string)), sheetname=observations_sheet)

    print('2')

    significant_proteins_df = fs.get_significant_proteins_dash(samples_df=samples_df, observations_df=observations_df)
    by_protein_up, by_protein_down = fs.get_significant_proteins_summary(significant_proteins_df)

    print('3')

    graph1 = fs.draw_summary_graph(by_protein_up, 'up_regulated')
    graph2 = fs.draw_summary_graph(by_protein_down, 'down_regulated')

    print('4')

    return html.Div([
    html.H2('up-regulated antibodies'),
    dt.DataTable(rows=by_protein_up.to_dict('records')),
    html.Hr(),
    html.H2('down-regulated antibodies'),
    dt.DataTable(rows=by_protein_down.to_dict('records')),
    html.Hr(),
    dcc.Graph(id='up-regulated', figure=graph1),
    html.Hr(),
    dcc.Graph(id='down-regulated', figure=graph2),
    html.Hr(),
    html.H2('observations data'),
    dt.DataTable(rows=observations_df.to_dict('records')),
    html.Hr(),
    html.H2('samples data'),
    dt.DataTable(rows=samples_df.to_dict('records'))
    ])


@app.callback(Output(component_id='output-data-upload', component_property='children'),
          [
            Input('upload', 'contents')
          ])
def populate_tables_callback(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        children = populate_tables(content_string=content_string)
        print('5')
        return children


# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8051
    )