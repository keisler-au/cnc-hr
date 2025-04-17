from datetime import datetime
import pandas as pd

from constants import REQUIRED_FILES


class StaffDocumentProcessor():
    def __init__(self, staff_reference, all_docs):
        self.reference_df = pd.read_csv(staff_reference, skiprows=2, header=None)
        self.docs_df = pd.read_csv(all_docs, skiprows=1, encoding_errors="ignore")
        self.staff_col = 'Client Surname'
        self.doc_col = 'Document Name'

    def mask_na_files(self, file_column):
        staff_role = self.staff_roles[file_column.name]
        required_files = REQUIRED_FILES['all_staff'] + REQUIRED_FILES[staff_role]
        return {
            file: 'N/A' if file not in required_files else file_column[file]
            for file in file_column.index
        }
    
    def set_relevant_docs(self):
        required_files = '|'.join(REQUIRED_FILES.values())
        staff_members = '|'.join(self.reference_df.iloc[1])
        filtered_files = self.docs_df[self.doc_col].str.contains(
            required_files, case=False, na=False
        )
        filtered_staff = self.docs_df[self.staff_col].str.contains(
            staff_members, case=False, na=False
        )
        self.docs_df = self.docs_df[filtered_files & filtered_staff]
        return self

    def set_staff_roles(self):
        def format_role(r):
            role = 'ot'
            if 'speech' in r: role = 'speech'
            elif 'admin' in r or 'reception' in r: role = 'admin'
            return role
        self.reference_df = self.reference_df.set_index(0)
        staff = list(self.reference_df.loc['Surname'])
        roles = self.reference_df.loc['Position'].ffill().tolist()[1:]
        formatted_roles = [format_role(role.lower()) for role in roles]
        self.staff_roles = dict(zip(staff, formatted_roles))
        return self

    def create_results_df(self):
        full_names = self.reference_df.iloc[0] + self.reference_df.iloc[1]
        self.results_df =  pd.DataFrame(columns=full_names)
        file_column_header = 'Files (based on keywords)'
        self.results_df[file_column_header] = list(REQUIRED_FILES.values())
        self.results_df.set_index(file_column_header, inplace=True)
        return self

    def fill_cells(self):
        for _, row in self.docs_df.iterrows():
            staff_name = f'{row['Client Firstname']} {row[self.staff_col]}'
            doc_name = row[self.doc_col].lower()
            for required_file in self.results_df.index:
                if required_file.lower() in doc_name:
                    try:
                        _, expiry = doc_name.split('_')
                    except ValueError:
                        expiry = None
                    today = pd.Timestamp.today() + pd.DateOffset(days=1)
                    in_one_month = pd.Timestamp.today + pd.DateOffset(months=1)
                    status = 'Yes'
                    if not expiry or expiry < today:
                        status = 'Expired'
                    elif expiry < in_one_month :
                        status = 'Expiring'
                    self.results_df.at[required_file, staff_name] = status
        return self.results_df.apply(self.mask_na_files).fillna("Missing").replace("Yes", "")
            
    def get_results(self):   
        return ( 
            self.set_relevant_docs()
                .set_staff_roles()
                .create_results_df()
                .fill_cells()
        )