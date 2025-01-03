# London Eye Reviews Sentiment Analysis App

This Streamlit app analyzes sentiment data for reviews and keywords associated with the London Eye. The app provides visualizations such as sentiment distributions, top keywords, and word clouds. It is intended for deployment within **Keboola Projects' Data Apps**, but it can also be run locally with some adjustments.

## Features

- **Sentiment Analysis Visualization**:
  - Displays sentiment score distributions and sentiment categories for reviews.
- **Keyword Analysis**:
  - Shows top keywords by frequency and a word cloud representation.
- **Filters**:
  - Filter reviews and keywords by sentiment score, review source, and date range.
- **Interactive Table**:
  - Editable table displaying detailed review data.

## Prerequisites

1. **Python Environment**:
   - Install Python (version 3.8 or higher recommended).
   - Install the required libraries using the command:

     ```bash
     pip install -r requirements.txt
     ```

2. **Secrets Configuration**:
   - Create a `secrets.toml` file in the `.streamlit/` directory with the following structure:

     ```toml
     [secrets]
     KBC_TOKEN = "<YOUR_KEBOOLA_STORAGE_API_TOKEN>"
     KBC_URL = "<YOUR_KEBOOLA_PROJECT_HOSTNAME>"
     ```

3. **Modify Table IDs**:
   - Update the table IDs in the `read_data()` function in the app script (`app.py`) to point to the correct Keboola tables if running locally:

     ```python
     data = read_data('<your_table_id_for_reviews>')
     keywords = read_data('<your_table_id_for_keywords>')
     ```

## Running the App Locally

To run the app locally:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3.	Add the secrets.toml file in the .streamlit/ directory as described above.

4.	Start the Streamlit app:
    ```bash
    streamlit run app.py
    ```

## Customization Notes
- Table IDs:
  - Ensure the read_data() function points to the correct Keboola table IDs. Modify the IDs in the app script as needed for your data.
- Visualizations:
  - The app uses static assets (e.g., keboola_logo.png and london_eye_wc.png). Replace these files in the static/ directory if custom branding or visualizations are required.

# Support
If you encounter any issues, please reach out to your Keboola project administrator or contact support at support@keboola.com.
