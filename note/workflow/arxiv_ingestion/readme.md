```
arxiv_ingestion/
├─ flows/
│  └─ daily_flow.py         # Prefect flow 定義
├─ tasks/
│  ├─ environment.py        # setup_environment task
│  ├─ fetch.py              # fetch_daily_papers task
│  ├─ pdf_retry.py          # process_failed_pdfs task
│  ├─ opensearch.py         # create_opensearch_placeholders task
│  ├─ report.py             # generate_daily_report task
│  └─ cleanup.py            # cleanup_temp_files task
├─ services/
│  ├─ arxiv_client.py       # 封裝 ArxivClient
│  ├─ pdf_parser.py         # PDF parsing service
│  └─ metadata_fetcher.py   # MetadataFetcher service
├─ db/
│  └─ factory.py            # Database session / ORM
└─ main.py                  # CLI 或直接觸發 flow

```