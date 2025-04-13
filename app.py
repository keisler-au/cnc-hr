import streamlit as st

from processor import StaffDocumentProcessor

# change mine and kates documents in the downloaded echidna .csv
# upload to stream lit
# give it a crack

st.title("Staff File Checker")
reference_file_upload = st.file_uploader("Upload staff reference file | .csv", type="csv")
staff_documents_upload = st.file_uploader("Upload staff documents file | .csv", type="csv")
check_files_button = st.button("Check files")

if check_files_button and (not reference_file_upload or not staff_documents_upload):
    st.info("Please upload both CSV files")
elif check_files_button:
    processor = StaffDocumentProcessor(
        reference_doc= "staff_references.csv",
        files_doc="staff_documents.csv"
    )

    result_df =  processor.get_results()
    

    st.write("Results:")
    st.dataframe(result_df)

    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Results CSV",
        data=csv,
        file_name="staff_file_status.csv",
        mime="text/csv"
    )

        