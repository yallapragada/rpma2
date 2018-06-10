# this version of the app has a upload file

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import io
import base64
import find_significant as fs

samples_sheet = 'SAMPLES'
observations_sheet = 'OBSERVATIONS'
antibodies_sheet = 'ANTIBODIES'

app = dash.Dash()
app.scripts.config.serve_locally = True
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

app.layout = html.Div([
    html.H2('Analysis of RPMA Data', style={'text-align': 'center'}),
    html.Div([dcc.Upload(html.Button('Upload File'), id='upload', style={'text-align': 'center'})]),

    html.Div([
        html.Pre(id='slider-pre'),
        html.Div(dcc.Slider(id='slider'), style={'display': 'none'})
    ]),

    html.Div([
        html.Pre(id='table1-pre'),
        html.Div([
            html.Div([
                html.Div(
                    dt.DataTable(rows=[{}], id='table1a', row_selectable=True), style={'display': 'none'},
                    className='three columns'
                ),
                html.Div(
                    dt.DataTable(rows=[{}], id='table1b', row_selectable=True), style={'display': 'none'},
                    className='three columns'
                )
            ], className="row "),
            html.Pre(id='empty-line1'),
            html.Div(
                html.Button(id='submit-button'), style={'display': 'none', 'text-align': 'center'},
                className='two columns'
            )
        ])
    ]),

    html.Div([
        html.Pre(id='table2-pre'),
        html.Div([
            html.Pre(id='empty-line2'),
            html.Div(
                dt.DataTable(rows=[{}], id='table2', row_selectable=True, filterable=True, sortable=True),
                style={'display': 'none'}, className='seven columns'
            ),
        ])
    ]),

    html.Div([
        html.Pre(id='antibody-graph-pre'),
        html.Div([
            html.Pre(id='empty-line3'),
            html.Div(
                dcc.Graph(id='antibody-graph'),
            ),
        ])
    ]),

    html.Div([
        html.Div(id='hidden-div1', style={'display': 'none'})
    ]),
    html.Div([
        html.Div(id='hidden-div2', style={'display': 'none'})
    ]),
    html.Div([
        html.Div(id='hidden-div3', style={'display': 'none'})
    ]),
    html.Div([
        html.Div(id='hidden-div4', style={'display': 'none'})
    ])
], className='container')


@app.callback(Output('hidden-div2', 'children'),
              [Input('upload', 'contents')])
def populate_hidden_div(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        samples_df = pd.read_excel(io.BytesIO(base64.b64decode(content_string)), sheetname=samples_sheet)
        print(samples_df.head())
        return samples_df.to_json(date_format='iso', orient='split')


@app.callback(Output('hidden-div3', 'children'),
              [Input('upload', 'contents')])
def populate_hidden_div(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        observations_df = pd.read_excel(io.BytesIO(base64.b64decode(content_string)), sheetname=observations_sheet)
        print(observations_df.head())
        return observations_df.to_json(date_format='iso', orient='split')


@app.callback(Output('hidden-div4', 'children'),
              [Input('upload', 'contents')])
def populate_hidden_div(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        antibodies_df = pd.read_excel(io.BytesIO(base64.b64decode(content_string)), sheetname=antibodies_sheet)
        return antibodies_df.to_json(date_format='iso', orient='split')


@app.callback(Output(component_id='slider-pre', component_property='children'),
              [Input('upload', 'contents')])
def show_slider(contents):
    if contents is not None:
        slider_marks = {}
        marks = 1.25
        end_marks = 4.0
        while marks <= end_marks:
            slider_marks[marks] = format(marks, '.2f')
            marks += 0.25
        print(slider_marks)

        heading_slider = html.H6('Regulation factor', className="gs-header gs-text-header padded")
        slider = html.Div(dcc.Slider(id='slider', min=1.0, max=4.0, step=0.25, value=1.0, updatemode='mouseup',
                                     marks=slider_marks))
        empty_line_slider = html.Br(id='empty-line-slider')
        hr = html.Hr(id='horizontal-line')
        slider_div = html.Div([empty_line_slider, heading_slider, slider, empty_line_slider, hr])
        return slider_div


@app.callback(Output(component_id='table1-pre', component_property='children'),
              [
                  Input('slider', 'value')
              ],
              [
                  State('hidden-div2', 'children'),
                  State('hidden-div3', 'children')
              ])
def populate_table1(value, samples_json, observations_json):
    if value is not None and samples_json is not None and observations_json is not None:
        observations_df = pd.read_json(observations_json, orient='split')
        samples_df = pd.read_json(samples_json, orient='split')
        significant_proteins_df = fs.get_significant_proteins_dash(samples_df=samples_df, observations_df=observations_df, regulation_factor=value)
        by_protein_up, by_protein_down = fs.get_significant_proteins_summary(significant_proteins_df)

        table1a_div = html.Div(dt.DataTable(rows=by_protein_up.to_dict('records'), row_selectable=True, id='table1a'))
        table1b_div = html.Div(dt.DataTable(rows=by_protein_down.to_dict('records'), row_selectable=True, id='table1b'))

        heading1a = html.H3('Up-regulated antibody targets', className="gs-header gs-text-header padded")
        heading1b = html.H3('Down-regulated antibody targets', className="gs-header gs-text-header padded")
        table_div = html.Div([heading1a, table1a_div, heading1b, table1b_div])
        button = html.Button(id='submit-button', n_clicks=0, children='Submit')
        button_div = html.Div(button, style={'text-align': 'right'})
        pre = html.Pre(id='empty-line1')
        return_div = html.Div([table_div, pre, button_div])
        return return_div


# to populate a hidden-div1 that contains significant proteins dataframe
# we need hidden-div1 to populate table2
@app.callback(Output(component_id='hidden-div1', component_property='children'),
              [
                  Input('slider', 'value')
              ],
              [
                  State('hidden-div2', 'children'),
                  State('hidden-div3', 'children')
              ])
def populate_hidden_div1(value, samples_json, observations_json):
    if value is not None and observations_json is not None and samples_json is not None:
        observations_df = pd.read_json(observations_json, orient='split')
        samples_df = pd.read_json(samples_json, orient='split')
        significant_proteins_df = fs.get_significant_proteins_dash(samples_df=samples_df, observations_df=observations_df, regulation_factor=value)
        return significant_proteins_df.to_json(date_format='iso', orient='split')

# populate table2
# we need hidden-div4 (antibodies df) to create a href with right url
@app.callback(Output(component_id='table2-pre', component_property='children'),
              [
                  Input('submit-button', 'n_clicks')
              ],
              [
                  State('table1a', 'rows'),
                  State('table1a', 'selected_row_indices'),
                  State('table1b', 'rows'),
                  State('table1b', 'selected_row_indices'),
                  State('hidden-div1', 'children'),
                  State('hidden-div4', 'children')
              ])
def update_table(n_clicks, rows1a, selected_row_indices1a, rows1b, selected_row_indices1b, sig_proteins_json, antibodies_json):
    print("*************************")
    if sig_proteins_json is not None and selected_row_indices1a is not None and len(selected_row_indices1a) > 0:
        value = rows1a[selected_row_indices1a[0]]['name']
        significant_proteins_df = pd.read_json(sig_proteins_json, orient='split')
        antibodies_df = pd.read_json(antibodies_json, orient='split')
        protein_df = significant_proteins_df.loc[significant_proteins_df['name'] == value]
        cols = ['name', 'sample', 'cell_type', 'strain', 'concentration', 'time', 'value', 'ratio']
        protein_df = protein_df[cols]
        table_div = html.Div(dt.DataTable(rows=protein_df.to_dict('records'), id='table2', row_selectable=True, filterable=True, sortable=True))
        pre = html.Pre(id='empty-line2')
        heading1a = html.H6(create_link(value,antibodies_df), className="gs-header gs-text-header padded")
        graph = dcc.Graph(figure=fs.draw_antibody_graph(df=protein_df), id='antibody-graph')
        graph_div = html.Div(graph)
        return_div = html.Div([pre, heading1a, table_div, pre, graph_div])
        return return_div
    if sig_proteins_json is not None and selected_row_indices1b is not None and len(selected_row_indices1b) > 0:
        value = rows1b[selected_row_indices1b[0]]['name']
        significant_proteins_df = pd.read_json(sig_proteins_json, orient='split')
        antibodies_df = pd.read_json(antibodies_json, orient='split')
        protein_df = significant_proteins_df.loc[significant_proteins_df['name'] == value]
        cols = ['name', 'sample', 'cell_type', 'strain', 'concentration', 'time', 'value', 'ratio']
        protein_df = protein_df[cols]
        table_div = html.Div(dt.DataTable(rows=protein_df.to_dict('records'), id='table2', row_selectable=True, filterable=True, sortable=True))
        pre = html.Pre(id='empty-line2')
        heading1a = html.H6(create_link(value,antibodies_df), className="gs-header gs-text-header padded")
        graph = dcc.Graph(figure=fs.draw_antibody_graph(df=protein_df), id='antibody-graph')
        graph_div = html.Div(graph)
        return_div = html.Div([pre, heading1a, table_div, pre, graph_div])
        return return_div


@app.callback(Output(component_id='antibody-graph-pre', component_property='children'),
              [Input('table2', 'rows'),
               Input('table2', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    if rows is not None and len(rows) > 1:
        df = pd.DataFrame(rows)
        graph = dcc.Graph(figure=fs.draw_antibody_graph(df=df), id='antibody-graph')
        graph_div = html.Div(graph)
        pre = html.Pre(id='empty-line3')
        return_div = html.Div([pre, graph_div])
    else:
        pre = html.Pre(id='empty-line3')
        return_div = html.Div([pre])
    return return_div


def create_link(value, antibodies_df):
    print(value)
    antibody = antibodies_df.loc[antibodies_df['Antibody_Shortname'] == value]
    print(antibody)
    if antibody is not None:
        company = antibody['Company'].values[0]
        print(company)
        if company == 'CellSig':
            catalog_id = str(antibody['CatalogID'].values[0])
            print(catalog_id)
            url = 'http://www.cellsignal.com/product/productDetail.jsp?productId='+catalog_id
            print(url)
            link = html.A(href=url, children=value)
            print(link)
        else:
            link = value
    else:
        link = value
    return link


# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8053
    )
