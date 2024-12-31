import pandas as pd
import numpy as np

raw_data = pd.read_csv("arcgis_data.csv")
mill_rates_data = {
    'City': {
        'Agricultural': 0.011682,
        'Commercial and Industrial Class': 0.012353,
        'Residential': 0.008031,
        'Residential Condominium': 0.008031,
        'Multi-Residential': 0.008031
    },
    'Library': {
        'Agricultural': 0.001199,
        'Commercial and Industrial Class': 0.001268,
        'Residential': 0.000824,
        'Residential Condominium': 0.000824,
        'Multi-Residential': 0.000824
    },
    'Education': {
        'Agricultural': 0.00142,
        'Commercial and Industrial Class': 0.00686,
        'Residential': 0.00454,
        'Residential Condominium': 0.00454,
        'Multi-Residential': 0.00454
    }
}

mill_rates = pd.DataFrame(mill_rates_data)

residential = ['Residential', 'Residential Condominium',
                   'Vacant Residential Land', 'Multi-Residential']

commercial = ['Auto, Dealership', 'Auto, Mini-Lube Garage',
                  'Store, Market', 'Warehouse, Storage',
                  'Auto, Repair Garage', 'Auto, Showroom',
                  'Bank, Downtown Central', 'Commercial - General',
                  'Commercial - Non General',
                  'Commercial - Utility / Transportation',
                  'Vacant Commercial Land']

def calculate_taxable_value(df: pd.DataFrame)-> pd.DataFrame:

    conditions = [
        df['Property_Use_Cd_Grp_Desc'].isin(residential),
        df['Property_Use_Cd_Grp_Desc'].isin(commercial)
    ]
    choices = [
        df['Assessed_Value'] * 0.8,
        df['Assessed_Value'] * 0.85
    ]

    df['taxable_value'] = np.select(conditions, choices, default=df['Assessed_Value'])

    df['library_tax'] = 0.0
    df['education_tax'] = 0.0
    df['city_tax'] = 0.0

    def get_mill_rate_category(property_type: str)-> str:

        property_type = str(property_type).strip()

        if 'Agricultural' in property_type:
            return 'Agricultural'
        elif any(comm_type in property_type for comm_type in commercial):
            return 'Commercial and Industrial Class'
        elif 'Condominium' in property_type:
            return 'Residential Condominium'
        elif 'Multi-Residential' in property_type:
            return 'Multi-Residential'
        else:
            return 'Residential'

    for idx, row in raw_data.iterrows():
        mill_rate_category = get_mill_rate_category(row['Property_Use_Cd_Grp_Desc'])

        df.at[idx, 'library_tax'] = row['taxable_value'] * mill_rates.loc[mill_rate_category, 'Library']
        df.at[idx, 'education_tax'] = row['taxable_value'] * mill_rates.loc[mill_rate_category, 'Education']
        df.at[idx, 'city_tax'] = row['taxable_value'] * mill_rates.loc[mill_rate_category, 'City']


    df.loc[df['tax_total'].isna(), 'tax_total'] = df['library_tax'] + df['education_tax'] + df['city_tax']
    df = df.copy()
    df = df.dropna(subset=['tax_total'])
    df['tax_total'] = df['tax_total'].astype(int)

    return df

def export_as_csv(df: pd.DataFrame) -> None:
    df.to_csv('processed_data.csv', index=False, header=True)


def main() -> None:
    processed_data = calculate_taxable_value(raw_data)
    export_as_csv(processed_data)
    print(processed_data)

main()
