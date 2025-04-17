import streamlit as st

from processor import StaffDocumentProcessor


st.title("HR File Scanner")
staff_reference_file = st.file_uploader("Upload staff reference file | .csv", type="csv")
all_documents_file = st.file_uploader("Upload staff documents file | .csv", type="csv")
scan_button = st.button("Scan files")

if scan_button and (not staff_reference_file or not all_documents_file):
    st.info("Please upload both CSV files")
elif scan_button:
    processor = StaffDocumentProcessor(
        staff_reference=staff_reference_file,
        all_docs=all_documents_file
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

        