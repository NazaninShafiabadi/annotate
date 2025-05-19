import os
import argparse
import pandas as pd
from pathlib import Path
import streamlit as st


def create_parser():
    parser = argparse.ArgumentParser(description="Sentence Annotation Tool")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the CSV file containing sentences for annotation.")
    parser.add_argument("--output_file", type=str, required=True, help="Path to save the annotated sentences.")
    return parser


def load_data(file_path):
    if not file_path.endswith(".csv"):
        raise ValueError("Input file must be a CSV file.")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file {file_path} does not exist.")
    df = pd.read_csv(file_path)
    return df


def annotate(args):
    # Load data into session state
    if "df" not in st.session_state:
        st.session_state.df = load_data(args.input_file)

    # Track the current sentence index
    if "index" not in st.session_state:
        st.session_state.index = 0

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = st.session_state.df
    if "acceptable" not in df.columns:
        df["acceptable"] = None 
    if "suggestion" not in df.columns:
        df["suggestion"] = None

    # Display one sentence at a time
    index = st.session_state.index
    if index < len(df):
        row = df.iloc[index]

        st.subheader(f"Sentence {index + 1}")
        st.write(f"**Target:** {row['target']}")
        st.write(f"**Original:** {row['comment']}")
        st.write(f"**Stance:** {row['label']}")
        st.write(f"**Transformed:** {row['transformation']}")

        acceptable = st.radio(f"Does the transformation reflect the opposite stance?", ["Yes", "No"], key=f"radio_{index}")

        suggestion = None
        if acceptable == "No":
            suggestion = st.text_area(f"Provide a minimal transformation of the original statement that would reflect the opposite stance toward the given target:", 
                                      key=f"suggestion_{index}")

        if st.button("Submit Response"):
            df.at[index, "acceptable"] = acceptable
            df.at[index, "suggestion"] = suggestion
            df.to_csv(output_path, index=False)

            st.session_state.index += 1
            st.rerun()

    else:
        # st.success("Annotation complete! Thank you for your participation.")
        uploaded_file = st.file_uploader("Annotation complete! Please upload your annotated file here:")
        if uploaded_file:
            upload_path = Path("uploads") / uploaded_file.name
            upload_path.parent.mkdir(parents=True, exist_ok=True)
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ File received! Thank you for your participation.")


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    st.set_page_config(page_title="Statement Annotation Tool", layout="wide")
    annotate(args)
