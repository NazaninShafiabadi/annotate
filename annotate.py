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


def boxed_markdown(content):
    st.markdown(f"""
    <div style="background-color:#f9f9f9; padding: 15px; border-radius: 6px; border: 1px solid #ddd; margin-bottom: 20px;">
        {content}
    </div>
    """, unsafe_allow_html=True)


def annotate(args):
    st.set_page_config(page_title="Statement Annotation Tool", layout="wide")

    # Load data into session state
    if "df" not in st.session_state:
        st.session_state.df = load_data(args.input_file)

    if "index" not in st.session_state:
        st.session_state.index = 0

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = st.session_state.df
    if "acceptable" not in df.columns:
        df["acceptable"] = None 
    if "suggestion" not in df.columns:
        df["suggestion"] = None
    if "easy" not in df.columns:
        df["easy"] = None

    # Sidebar instructions
    st.sidebar.title("Task Instructions")
    st.sidebar.markdown("""
    - One statement will be displayed at a time.
    - Mark whether the transformation correctly reflects the **opposite stance**.
    - If not, suggest a better alternative.
    - Submit your response to save and move to the next statement.
    
    You can upload your annotated file at the end of the task. \n
    If you have any questions, please contact the administrator.
    """)

    # Main interface
    index = st.session_state.index
    if index < len(df):
        row = df.iloc[index]

        st.title("📚 Statement Annotation Tool")
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

        # Annotation input
        st.markdown(
            """
            <div style='margin-top:25px; margin-bottom:-30px'>
                <span style='font-size:18px; font-weight:600'>
                    Does the transformed statement minimally alter the original while accurately expressing the opposite stance?
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        acceptable = st.radio("Is the transformation acceptable?", 
                              ["Yes", "No"], 
                              label_visibility="hidden", 
                              key=f"acceptable_{index}"
                              )

        suggestion = None
        if acceptable == "No":
            with st.expander("✏️ Suggest a better transformation"):
                suggestion = st.text_area(
                    "Provide a minimal transformation of the original statement that would reflect the opposite stance toward the target:", 
                    key=f"suggestion_{index}")
                
                easy = st.radio("Was the transformation easy to perform?", ["Yes", "No"], key=f"easy_{index}")
        else:
            easy = None

        # Submit button
        col_submit, _ = st.columns([1, 4])
        if col_submit.button("Submit Response"):
            df.at[index, "acceptable"] = acceptable
            df.at[index, "suggestion"] = suggestion
            df.at[index, "easy"] = easy
            df.to_csv(output_path, index=False)

            st.session_state.index += 1
            st.rerun()

    else:
        st.title("🎉 Annotation Complete!")
        uploaded_file = st.file_uploader("📁 Please upload your annotated file here:")
        if uploaded_file:
            upload_path = Path("uploads") / uploaded_file.name
            upload_path.parent.mkdir(parents=True, exist_ok=True)
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ File received! Thank you for your participation.")


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    annotate(args)
