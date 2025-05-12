import argparse
import streamlit as st
import pandas as pd


def create_parser():
    parser = argparse.ArgumentParser(description="Sentence Annotation Tool")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the CSV file containing sentences for annotation.")
    parser.add_argument("--output_file", type=str, required=True, help="Path to save the annotated sentences.")
    return parser


def load_data(file_path):
    if not file_path.ends_with(".csv"):
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

        acceptability = st.radio(f"Does the transformation reflect the opposite stance?", ["Yes", "No"], key=f"radio_{index}")

        suggestion = None
        if acceptability == "No":
            suggestion = st.text_area(f"Suggest a better transformation:", key=f"suggestion_{index}")

        if st.button("Submit Response"):
            df.at[index, "acceptable"] = acceptability
            df.at[index, "suggestion"] = suggestion

            st.session_state.index += 1
            st.rerun()

    else:
        st.success("Annotation complete! You can now save your responses.")

    if st.session_state.index >= len(df) and st.button("Save Annotations"):
        df.to_csv(args.output_file, index=False)
        st.success("Annotations saved successfully!")


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    st.set_page_config(page_title="Sentence Annotation Tool", layout="wide")
    annotate(args)
