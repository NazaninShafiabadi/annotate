"""
This script is designed to verify the transformations made in the annotation process.
It allows the administrator to review the original statements, the transformations made, and decide which transformation to keep.
It also provides an option to suggest a better transformation if neither the model's nor the annotator's transformation is satisfactory.
The final verified transformations are saved to a specified output file.

Usage:
python verify.py --input_file <path_to_annotated_csv> --output_file <path_to_save_verified_transformations>
streamlit run verify.py -- \
--input_file "uploads/0_annoated.csv" \
--output_file "verified_annotations/0_verified.csv"
"""

import os
import argparse
import pandas as pd
from pathlib import Path
import streamlit as st


def create_parser():
    parser = argparse.ArgumentParser(description="Annotation Verification Tool")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the annotated CSV file.")
    parser.add_argument("--output_file", type=str, required=True, help="Path to save the final verified transformations.")
    return parser


def load_data(file_path):
    if not file_path.endswith(".csv"):
        raise ValueError("Input file must be a CSV file.")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file {file_path} does not exist.")
    df = pd.read_csv(file_path)
    return df


def boxed_markdown(content):
    st.markdown(f"""
    <div style="background-color:#f9f9f9; padding: 15px; border-radius: 6px; border: 1px solid #ddd; margin-bottom: 20px;">
        {content}
    </div>
    """, unsafe_allow_html=True)


def verify(args):
    st.set_page_config(page_title="Annotation Verification Tool", layout="wide")

    # Load data into session state
    if "df" not in st.session_state:
        st.session_state.df = load_data(args.input_file)

    if "index" not in st.session_state:
        st.session_state.index = 0

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = st.session_state.df

    # Prepare final df
    columns_to_keep = ['id', 'target', 'comment', 'label', 'language', 'dataset']
    out_df = df[columns_to_keep].copy()
    out_df['transformation'] = None

    # Main interface
    index = st.session_state.index
    if index < len(df):
        row = df.iloc[index]

        st.title("🔍 Annotation Verification Tool")
        st.markdown(f"#### 🔢 {index + 1} / {len(df)}")
        st.progress((index + 1) / len(df))

        # Statement info
        st.markdown("#### 🎯 Target Question")
        boxed_markdown(row["target"])

        st.markdown("#### 💬 Original Statement")
        boxed_markdown(row["comment"])

        st.markdown("#### ⚖️ Original Stance")
        boxed_markdown(row["label"])

        st.markdown("#### 🔁 Transformed Statement")
        boxed_markdown(row["transformation"])

        st.markdown("#### 💁🏻 Annotator Suggestion")
        boxed_markdown(row["suggestion"])

        # Action input
        transformation = None
        st.markdown("Which transformation do you want to keep?")
        cols = st.columns([0.35, 0.4, 2])
        with cols[0]:
            if st.button("Model"):
                transformation = row["transformation"]

        with cols[1]:
            if st.button("Annotator"):
                transformation = row["suggestion"]

        with cols[2]:
            if st.button("Neither"):
                with st.expander("✏️ Suggest a better transformation"):
                    transformation = st.text_area("", key=f"transformation_{index}")
                
        keep = st.radio("Do you want to keep this example?", ["Yes", "No"], key=f"keep_{index}")


        # Submit button
        col_submit, _ = st.columns([1, 4])
        if col_submit.button("Submit Response"):
            if keep == "Yes":
                out_df.at[index, "transformation"] = transformation
                out_df.to_csv(output_path, index=False)

            st.session_state.index += 1
            st.rerun()

    else:
        st.title("🎉 Verification Complete!")
        # uploaded_file = st.file_uploader("📁 Upload the verified file here:")
        # if uploaded_file:
        #     upload_path = Path("verified_annotations") / uploaded_file.name
        #     upload_path.parent.mkdir(parents=True, exist_ok=True)
        #     with open(upload_path, "wb") as f:
        #         f.write(uploaded_file.getbuffer())
        #     st.success("✅ File saved.")


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    verify(args)