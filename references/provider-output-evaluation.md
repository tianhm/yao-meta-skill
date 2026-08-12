# Provider Output Evaluation

The governed provider matrix lives at `evals/output/provider_matrix.json`. It fixes DeepSeek V4 Flash and DeepSeek V4 Pro, non-thinking mode, temperature 0, and 3,000 maximum output tokens. The matrix caps one evaluation at 40 provider calls, 250,000 total tokens, and 60 seconds per call. Only `DEEPSEEK_API_KEY` is read from the environment.

Run the matrix through the trusted evidence entrypoint:

```bash
python3 scripts/yao.py evidence-build . --run-id <run-id>
python3 scripts/yao.py evidence-build . --run-id <run-id> --publish
```

When the credential is missing, the run records `external-required` and keeps quality promotion pending. When the credential is present, the run executes 10 frozen cases across two models and two variants. Raw outputs stay under `.yao/runs/<run-id>/raw-outputs`. Committed or published reports contain hashes, provider and model metadata, observed tokens, duration, response identifiers, and a redacted structural summary.

Successful execution creates 20 shuffled A/B pairs and separate templates for Reviewer A, Reviewer B, and Reviewer C. Blind-pack entries contain randomized labels, hashes, and relative pointers into the run's `raw-outputs` directory; answer text is never copied into a report artifact or release bundle. Each reviewer completes all 20 pairs independently before the role mapping is opened. Adjudicate the three packets with:

```bash
python3 scripts/adjudicate_multi_reviewer.py \
  --answer-key reports/provider_output_answer_key.json \
  --decisions reports/provider_review_reviewer-a.json \
  --decisions reports/provider_review_reviewer-b.json \
  --decisions reports/provider_review_reviewer-c.json
```

Quality promotion requires at least 15 with-skill pair wins, at least 7 wins for each model's 10 pairs, zero critical failures, and Fleiss' kappa of at least 0.40. This promotion is internal quality evidence. The world-class ledger stays pending until its independent acceptance process is complete.

Model contract references: [DeepSeek Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/) and [DeepSeek API Changelog](https://api-docs.deepseek.com/updates/).
