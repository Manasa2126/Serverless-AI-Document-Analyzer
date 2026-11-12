# Serverless AI Document Analyzer

A serverless document-processing project built with AWS Lambda, Amazon S3 and Amazon Bedrock. An S3 upload event triggers a Lambda function, which reads a PDF, sends it to an Amazon Bedrock model for text extraction, and stores the extracted text as a JSON result in a separate S3 bucket.

## Architecture

```text
PDF uploaded
    |
    v
Amazon S3 (source bucket)
    |
    | Object-created event
    v
AWS Lambda (Python)
    |
    | Invoke model
    v
Amazon Bedrock (Amazon Nova Lite)
    |
    | Extracted text
    v
Amazon S3 (results bucket)
    |
    v
JSON output
```

## AWS services

- **Amazon S3** – stores source PDF documents and generated JSON results.
- **AWS Lambda** – processes S3 upload events and orchestrates the workflow.
- **Amazon Bedrock** – uses the configured foundation model to extract document text.
- **AWS IAM** – grants the Lambda execution role only the permissions needed to read source documents, invoke the model and write results.

### About Amazon Textract

The Lambda source file supplied for this repository sends the PDF directly to Amazon Bedrock. It does not currently make an Amazon Textract API call. If Textract is used elsewhere in your deployed workflow (for example, in another Lambda function or processing step), document that component separately and add its code/configuration before describing it as part of this function's execution path.

## Repository structure

```text
serverless-ai-document-analyzer/
├── src/
│   └── lambda_function.py
├── .gitignore
└── README.md
```

## Configuration

Set these environment variables on the Lambda function:

| Variable | Description | Example |
|---|---|---|
| `RESULTS_BUCKET` | S3 bucket where JSON results are written | Your results bucket name |
| `MODEL_ID` | Amazon Bedrock model ID | `amazon.nova-lite-v1:0` |

The Lambda function uses the AWS region configured for the Lambda runtime unless you explicitly configure a different Bedrock client region.

Do not commit real bucket names if you consider them sensitive. Never commit AWS access keys, secret keys, session tokens, passwords, API keys, private documents or `.env` files.

## Required permissions

Configure the Lambda execution role with appropriately scoped permissions for:

- Reading objects from the source S3 bucket (`s3:GetObject`).
- Writing result objects to the results S3 bucket (`s3:PutObject`).
- Invoking the selected Bedrock model (`bedrock:InvokeModel`).
- Writing logs to Amazon CloudWatch Logs.

Restrict resources to the specific buckets and model where practical. The role should not need embedded access keys.

## Deployment notes

1. Create or identify the source and results S3 buckets.
2. Configure an S3 `ObjectCreated` event notification to invoke the Lambda function.
3. Set the `RESULTS_BUCKET` environment variable and, optionally, `MODEL_ID`.
4. Confirm that the Lambda execution role has the permissions listed above.
5. Confirm that the selected Bedrock model is available in the Lambda's AWS region.
6. Upload a test PDF and verify that a corresponding `_results.json` object is created in the results bucket.

## Limitations and next improvements

- The current handler processes the first S3 record in an event.
- The current implementation is designed for PDF input.
- Add file-size validation, structured error handling, retry/idempotency controls and automated tests before using this in production.
- If using Amazon Textract in another part of the solution, document its exact role and add a sanitized example of that integration.

## Security

This repository intentionally does not include AWS credentials or account-specific deployment secrets. Use IAM execution roles and environment configuration rather than hard-coded credentials.
