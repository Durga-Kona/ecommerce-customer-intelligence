# GitHub + Streamlit Community Cloud Deployment

1. Create a GitHub repository and upload the project files while preserving folders. Do not upload `.venv`, secrets, or private data.
2. Confirm `requirements.txt`, `src/dashboard.py`, `ecommerce_dw.db`, `data/raw/`, and `outputs/` are committed. The included `.gitignore` intentionally does not ignore the sample database/output artifacts required for the initial demo.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Create an app from your repository and set main file path to `src/dashboard.py`.
5. Deploy, open the generated URL, and check all tabs and charts.
6. Test CSV import with copies of the six sample CSVs before trying a custom dataset.

## Persistence and privacy

The hosted app's writable filesystem is not guaranteed to persist across restarts/redeployments. Uploaded data changes the active raw CSVs, database and outputs on that instance, but may be lost. Keep original data safely elsewhere. Do not commit real personal data into a public repository. For durable multi-user imports, use persistent object storage or a hosted database and add access controls.

## Troubleshooting

- Build fails: inspect the Streamlit app logs and confirm package versions in `requirements.txt` are installable.
- Missing table/database: verify the database is committed and the repository includes the required schema and sample CSV files.
- Blank customer/product analytics: run `python -m src.run_all` locally and commit updated sample output files if you intentionally changed the sample dataset.
- Import succeeds but later disappears on cloud: this is the expected limitation of ephemeral local storage; use persistent storage for lasting uploads.
