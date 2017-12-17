
import pandas as pd
import sys


def read_excel(excel_file, sheetname):
    df = pd.read_excel(excel_file, sheetname=sheetname)
    return df


def get_untreated_sample_name(samples_df, treated_sample_name):
    time = samples_df.loc[:treated_sample_name]['TIME'].values[0]
    cell_type = samples_df.loc[:treated_sample_name]['CELL_TYPE'].values[0]
    untreated_sample_name = samples_df.index[(samples_df['TIME'] == time) & (samples_df['STRAIN'] == 'UNTREATED') & (samples_df['CELL_TYPE'] == cell_type)].values[0]
    return untreated_sample_name


def get_untreated_value(observations_df, column_name, untreated_sample_name):
    value = observations_df.loc[:untreated_sample_name][column_name].values[0]
    return float(value)


def process_observations(samples_df, observations_df):

    significant_proteins = {}

    column_names = list(observations_df.columns.values)

    for index, row in observations_df.iterrows():

        if str(index).startswith('RMH'):

            treated_sample_name = index
            treated_sample_name = str(treated_sample_name).split(' ')[0]+'-'+str(treated_sample_name).split(' ')[1]

            untreated_sample_name   = get_untreated_sample_name(samples_df=samples_df, treated_sample_name=treated_sample_name)

            tokens   = str(untreated_sample_name).split('-')
            untreated_sample_name   = tokens[0] + '-' + tokens[1] + ' ' + tokens[2] + ' '

            print(treated_sample_name, untreated_sample_name)

            for column_name in column_names:
                treated_value = float(row[column_name])
                untreated_value = get_untreated_value(observations_df=observations_df, column_name=column_name, untreated_sample_name=untreated_sample_name)
                ratio = treated_value / untreated_value
                if ratio > 2.0 or 1/ratio > 2.0:
                    significant_proteins[str(index).strip() + '|' + column_name] = ratio

    return significant_proteins


def run():
    excel_file          = sys.argv[1]
    samples_sheet       = sys.argv[2]
    observations_sheet  = sys.argv[3]
    samples_df          = read_excel(excel_file=excel_file, sheetname=samples_sheet)
    observations_df     = read_excel(excel_file=excel_file, sheetname=observations_sheet)
    samples_df          = samples_df.set_index('SAMPLE')
    observations_df     = observations_df.set_index('Sample')
    observations_df     = observations_df.rename(columns=lambda x: x.strip())
    significant_proteins = process_observations(samples_df=samples_df, observations_df=observations_df)

    for k, v in significant_proteins.items():
        print(k,v)


if __name__ == "__main__":
    run()