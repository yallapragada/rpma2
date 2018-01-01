# dash libs
import dash
import dash_html_components as html
import dash_core_components as dcc
import find_significant as fs


excel_file = 'C:\\Users\\uday\\pycharm_projects\\rpma2\\data\\rpma_data_yp_full.xls'
samples_sheet = 'YP_SAMPLES'
obsevations_sheet = 'YP'


# Data Analysis / Model
def fetch_all_data():
    significant_proteins_df = fs.get_significant_proteins(excel_file=excel_file,
                                                       samples_sheet=samples_sheet,
                                                       observations_sheet=obsevations_sheet)
    return significant_proteins_df


def fetch_summary_data(significant_proteins_df):
    by_protein_up, by_protein_down = fs.get_significant_proteins_summary(significant_proteins_df)
    return by_protein_up, by_protein_down


significant_proteins_df = fetch_all_data()
by_protein_up, by_protein_down = fetch_summary_data(significant_proteins_df=significant_proteins_df)
graph1 = fs.draw_summary_graph(by_protein_up, 'up_regulated')
graph2 = fs.draw_summary_graph(by_protein_down, 'down_regulated')

# Dashboard Layout / View
# Set up Dashboard and create layout
def generate_table(dataframe):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(len(dataframe))]
    )

app = dash.Dash()
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

app.layout = html.Div([
    html.Div([
        html.H1('Analysis of RPMA Data')
    ]),

    html.Div([
        html.Div([
            html.H2('up-regulated antibodies'),
            html.Div(
            generate_table(by_protein_up),
            className='three columns'),
            ], className='four columns'),
        html.Div([
            html.H2('down-regulated antibodies'),
            html.Div(
            generate_table(by_protein_down),
            className='three columns'),
            ], className = 'four columns'),
        html.Div([
            dcc.Graph(id='up-regulated', figure=graph1),
            dcc.Graph(id='down-regulated', figure=graph2),
        ],className = 'eight columns')
    ])
])


# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )