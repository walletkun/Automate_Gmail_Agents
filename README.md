# email-agent

## setup
    uv sync
    cp .env.example .env      # add your key
    # download a few .eml files from Gmail into fixtures/

## run
    uv run main.py fixtures/your-email.eml

## build order
Each session ends with something that runs. Never be in a state
where nothing works and you don't know why.

1. ingest + classify, one fixture           <- YOU ARE HERE
2. agent while-loop + Tavily search tool
3. second agent, string passed between them
4. markdown synthesis + prefs.json
5. swap fixtures for live Gmail (OAuth)

## the point
Instrument everything. Print the messages array every loop iteration in
session 2. Break tools on purpose and watch what the model does. Run the
same fixture five times and diff the output -- that variance is why
evals exist.
