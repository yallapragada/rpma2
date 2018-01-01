import pandas as pd
import sys
import plotly.graph_objs as go


def read_excel(excel_file, sheetname):
    df = pd.read_excel(excel_file, sheetname=sheetname)
    return df


def get_untreated_sample_name(samples_df, treated_sample_name):
    treated_sample = samples_df.loc[treated_sample_name]
    if treated_sample['STRAIN'] == 'UNTREATED':
        return treated_sample_name
    else:
        time = treated_sample['TIME']
        cell_type = treated_sample['CELL_TYPE']
        untreated_sample = samples_df[(samples_df['TIME'] == time) & (samples_df['STRAIN'] == 'UNTREATED') & (samples_df['CELL_TYPE'] == cell_type)]
        untreated_sample_name = untreated_sample.index.values[0]
        return untreated_sample_name


def get_untreated_value(observations_df, column_name, untreated_sample_name):
    value = observations_df.loc[untreated_sample_name][column_name]
    return float(value)


def process_observations(samples_df, observations_df):
    significant_proteins = []

    column_names = list(observations_df.columns.values)

    for index, row in observations_df.iterrows():

        if str(index).startswith('RMH'):

            treated_sample_name = index
            treated_sample_name = str(treated_sample_name).split(' ')[0] + '-' + str(treated_sample_name).split(' ')[1]

            untreated_sample_name = get_untreated_sample_name(samples_df=samples_df,
                                                              treated_sample_name=treated_sample_name)

            if treated_sample_name == untreated_sample_name:
                continue

            tokens = str(untreated_sample_name).split('-')
            untreated_sample_name = tokens[0] + '-' + tokens[1] + ' ' + tokens[2] + ' '

            for column_name in column_names:
                significant_protein = {}
                treated_value = float(row[column_name])
                untreated_value = get_untreated_value(observations_df=observations_df, column_name=column_name,
                                                      untreated_sample_name=untreated_sample_name)

                if float(untreated_value) < 1.0:
                    continue

                ratio = treated_value / untreated_value
                if ratio > 2.0 or 1 / ratio > 2.0:
                    significant_protein['name'] = column_name
                    significant_protein['sample'] = str(index).strip()
                    significant_protein['ratio'] = format(ratio, '.3f')
                    significant_proteins.append(significant_protein)

    significant_proteins = sorted(significant_proteins, key=lambda k: k['name'])
    significant_proteins_df = pd.DataFrame(significant_proteins)
    significant_proteins_df['ratio'] = pd.to_numeric(significant_proteins_df['ratio'], errors='coerce').fillna(0)
    return significant_proteins_df


def get_significant_proteins(excel_file, samples_sheet, observations_sheet):
    samples_df = read_excel(excel_file=excel_file, sheetname=samples_sheet)
    observations_df = read_excel(excel_file=excel_file, sheetname=observations_sheet)
    samples_df = samples_df.set_index('SAMPLE')
    observations_df = observations_df.set_index('Sample')
    observations_df = observations_df.rename(columns=lambda x: x.strip())
    significant_proteins_df = process_observations(samples_df=samples_df, observations_df=observations_df)
    return significant_proteins_df


def get_significant_proteins_summary(significant_proteins_df):
    by_protein_up = significant_proteins_df[(significant_proteins_df['ratio'] > 1.0)].groupby(by=['name']).agg({'name':'count', 'ratio':'mean'})
    by_protein_down = significant_proteins_df[(significant_proteins_df['ratio'] < 1.0) & (significant_proteins_df['ratio'] > 0.0)].groupby(by=['name']).agg({'name':'count', 'ratio':'mean'})
    by_protein_up.columns = ['count', 'mean']
    by_protein_down.columns = ['count', 'mean']
    by_protein_up.sort_values(['count'],ascending=False, inplace=True)
    by_protein_down.sort_values(['count'],ascending=False, inplace=True)
    by_protein_up.reset_index(level=0, inplace=True)
    by_protein_down.reset_index(level=0, inplace=True)
    return by_protein_up, by_protein_down


def draw_summary_graph(by_protein_up_or_down, title):
    proteins    = by_protein_up_or_down['name'][:10]
    counts      = by_protein_up_or_down['count'][:10]
    print(proteins)
    print(counts)

    figure = go.Figure(
        data = [
            go.Scatter(x=proteins, y=counts, mode='lines+markers')
        ],
        layout=go.Layout(
            title=title,
            showlegend=False
        )
    )
    return figure


def print_significant_proteins(significant_proteins_df):
    for index, row in significant_proteins_df.iterrows():
        print(row)


def run():
    excel_file = sys.argv[1]
    samples_sheet = sys.argv[2]
    observations_sheet = sys.argv[3]
    significant_proteins_df = get_significant_proteins(excel_file=excel_file,
                                                    samples_sheet=samples_sheet,
                                                    observations_sheet=observations_sheet)
    get_significant_proteins_summary(significant_proteins_df=significant_proteins_df)


#if __name__ == "__main__":
#    run()