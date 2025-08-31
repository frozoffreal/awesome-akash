# PostgreSQL with Backup to Storj on Akash

A complete solution for deploying a PostgreSQL database on Akash Network with automated backups to decentralized [Storj](https://www.storj.io/) storage.

## Architecture
This deployment consists of two services:
- PostgreSQL Database - Main database service
- Backup Agent - Python service that periodically backs up the database to Storj. The backup interval is configurable through the `BACKUP_INTERVAL_SECONDS` environment variable.

## Prerequisites
- Akash wallet with sufficient funds
- [Storj](https://www.storj.io/) account with access keys and bucket created
- Docker image: `frozoff/postgres-storj-backup:1.0.2`

## Deployment Steps
1. Go to [Akash Console](https://console.akash.network/) and connect your wallet
2. Deploy → "Run Custom Container"
3. Paste [this YAML](https://raw.githubusercontent.com/frozoffreal/awesome-akash/refs/heads/postgres-storj-backup/postgres-storj-backup/deploy.yaml) with your environment variables
4. Review bids and accept best offer
5. Wait for deployment to complete
6. Open "Logs tab" under service `postgres-backup` to see the backup process

## SHM usage
SDL with Postgres service with Shared Memory (SHM) enabled can be found [here](https://raw.githubusercontent.com/frozoffreal/awesome-akash/refs/heads/postgres-storj-backup/postgres-storj-backup/deploy-shm.yaml). For more information on SHM class storage, see the [Akash documentation](https://akash.network/docs/getting-started/stack-definition-language/#shared-memory-shm).
