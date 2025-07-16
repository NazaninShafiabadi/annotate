"""
This script is designed to verify the transformations made in the annotation process.
It allows the administrator to review the original statements, the transformations made, and decide which transformation to keep.
It also provides an option to suggest a better transformation if neither the model's nor the annotator's transformation is satisfactory.
The final verified transformations are saved to a specified output file.

Usage:
python verify.py --input_file <path_to_annotated_csv> --output_file <path_to_save_verified_transformations>
streamlit run verify.py -- \
--input_file "uploads/11_annotated.csv" \
--output_file "verified_annotations/11_verified_2.csv"
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

    # Prepare final df
    if "out_df" not in st.session_state:
        columns_to_keep = ['id', 'target', 'comment', 'label', 'language', 'dataset']
        st.session_state.out_df = st.session_state.df[columns_to_keep].copy()
        st.session_state.out_df['transformation'] = None

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = st.session_state.df
    out_df = st.session_state.out_df

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

        difficulty = (
            "Not specified" if "easy" not in row or pd.isna(row["easy"])
            else row["easy"].replace("Yes", "Low").replace("No", "High")
        )
        st.markdown(f"#### 🛠️ Difficulty Level: {difficulty}")

        # Action input
        st.markdown("Do you want to keep this example?")
        keep = st.radio(
            "Do you want to keep this example?",
            ["No", "Yes"],
            key=f"keep_{index}",
            label_visibility="collapsed"
        )

        if keep == "Yes":
            st.markdown("Which transformation do you want to keep?")
            transformation_choice = st.radio(
                "Select transformation source:",
                ["Model", "Annotator", "Neither"],
                key=f"choice_{index}",
                label_visibility="collapsed"
            )

            suggestion = ""
            if transformation_choice == "Neither":
                with st.expander("✏️ Suggest a better transformation"):
                    suggestion = st.text_area(
                        "Type your suggested transformation below.", 
                        label_visibility="collapsed", 
                        key=f"suggestion_{index}"
                    )

        if st.button("Submit Response", key=f"submit_{index}"):
            if keep == "Yes":
                if transformation_choice == "Model":
                    transformation = row["transformation"]
                elif transformation_choice == "Annotator":
                    transformation = row["suggestion"]
                elif transformation_choice == "Neither":
                    transformation = suggestion
                else:
                    transformation = None

                out_df.at[index, "transformation"] = transformation
            else:
                out_df.drop(index, inplace=True)
            
            out_df.to_csv(output_path, index=False)
            st.session_state.index += 1
            st.rerun()

    else:
        st.title("🎉 Verification Complete!")


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    verify(args)