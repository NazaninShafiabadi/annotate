# Statement Annotation Tool

## Annotation Process
One statement will be displayed at a time.

You should mark whether the transformation correctly reflects the opposite stance with respect to the target.

If the transformation is not acceptable, you should suggest a better alternative.

Once your response is submitted, it will be saved and the next statement will appear.

## Usage
Install Streamlit:
```
pip install streamlit
```
Run the tool using Streamlit:
```
streamlit run annotate.py -- \
--input_file "data/<num>.csv" \
--output_file "annotated/<num>_annotated.csv"
```
