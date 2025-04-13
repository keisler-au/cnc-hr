from datetime import datetime
import pandas as pd

from constants import REQUIRED_FILES

class StaffDocumentPrepocessor:
    def __init__(self, reference_doc):
        self.reference_doc_df = pd.read_csv(reference_doc, header=None)
        self.staff_details = self.get_staff_details()

    def get_staff_names(self):
        first_names = self.reference_doc_df.iloc[1]
        last_names = self.reference_doc_df.iloc[0]
        return [
            f"{first_name.strip()} {last_name.strip()}" 
            for first_name, last_name in zip(first_names, last_names)
        ]

    def get_job_positions(self):
        file_type_column = self.reference_doc_df.iloc[:, 0].astype(str).str.strip().str.lower()
        print(f'file_types: {file_type_column}')
        job_position_index = file_type_column[file_type_column == 'Position'].index
        assert not job_position_index.empty
        job_position_index = job_position_index[0]
        assert job_position_index
        positions = self.reference_doc_df.iloc[1:, job_position_index]

        def allocation(p):
            position = 'ot'
            if 'speech' in p: position = 'speech'
            elif 'admin' in p: position = 'admin'
            return position

        positions = [allocation(p.lower()) for p in positions]
        print(f'positions: {positions}')
        return positions

    def get_staff_details(self):
        staff_names = self.get_staff_names()
        job_positions = self.get_job_positions()
        print(f'staff_names: {staff_names}\njob_positions: {job_positions}')
        return dict(zip(staff_names, job_positions))


class StaffDocumentProcessor(StaffDocumentPrepocessor):
    def __init__(self, reference_doc, files_doc):
        super().__init__(reference_doc)
        self.fullname_header = "Full Name"
        self.document_header = "Document Name"
        self.df = pd.read_csv(files_doc, skiprows=1)

    def create_fullname_column(self):
        self.df[self.fullname_header] = (
            self.df["Client Firstname"].str.strip() 
            + " " 
            + self.df["Client Surname"].str.strip()
        )
        return self

    def filter_for_staff_personel(self):
        staff_names = set(self.staff_details.keys())
        self.df = self.df[self.df[self.fullname_header].isin(staff_names)]
        return self

    def filter_for_required_files(self):
        allowed = set(self.required_files["all_staff"] + sum(self.required_files.values(), []))
        self.df = self.df[self.df[self.document_header].isin(allowed)]
        return self

    def parse_file_names(self):
        self.df[["file_name", "file_date"]] = self.df[self.document_header].str.extract(
            r"^(.*)_(\d{2}-\d{2}-\d{4})$"
        )
        self.df = self.df.dropna(subset=["file_name", "file_date"])
        self.df["file_date"] = pd.to_datetime(
            self.df["file_date"], format="%d-%m-%Y", errors="coerce"
        )
        self.df = self.df.dropna(subset=["file_date"])
        return self
    
    def check_staff_documents(self):
        df = self.df
        today = pd.Timestamp.today()
        results = []

        for user in df[self.fullname_header].unique():
            print(f'user: {user}')
            print(f'user_row? : {df[self.fullname_header] == user}')
            print(f'user_df: {df[df[self.fullname_header] == user]}')
            user_df = df[df[self.fullname_header] == user]
            user_files = set(user_df["file_name"])

            users_required_files = (
                REQUIRED_FILES["all_staff"] + REQUIRED_FILES[self.staff_details[user]]
            )
            print(f'users_required_files: {users_required_files}')
            
            row = { "Staff": user }
            missing_files = users_required_files - user_files
            for file in missing_files:
                row["FileName"] = file
                row["Status"] = "missing"
                results.append(row)

            for _, file_row in user_df.iterrows():
                if file_row["file_date"] < today: 
                    row["FileName"] = file_row["file_name"]
                    row["Status"] = "expired"
                    results.append(row)

        return results
    
    def get_results(self):
        return (
            self.create_fullname_column()
            .filter_for_staff_personel()
            .filter_for_required_files()
            .parse_file_names()
            .check_staff_documents()
        )