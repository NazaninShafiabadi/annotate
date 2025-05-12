# Sentence Annotation Tool

## Annotation Process
One sentence will be displayed at a time.

You should mark whether the transformation correctly reflects the opposite stance with respect to the target.

If the transformation is not acceptable, you should suggest a better alternative.

Once your response is submitted, the next sentence will be displayed.

## Usage
Run the tool using Streamlit:
```
streamlit run annotate.py -- \
--input_file "fr_sample.csv" \
--output_file "fr_sample_annotated.csv"
```

## Dependencies
This tool requires:
- **pandas**
- **streamlit**

Install them using:
```
pip install pandas streamlit
```
or
```
pip install -r requirements.txt
```
