# Project Quant-FX

PythonによるFX自動売買システム（OANDA v20 API対応）。
現在は **Mock Mode（模擬モード）** により、APIトークンなしでも動作確認やバックテストが可能です。

## 特徴
- **OANDA v20 API**: OANDA Japanの本番/デモ口座に対応（予定）。
- **Mock Mode**: 仮想データと仮想注文によるデモ動作が可能。
- **Backtesting**: 過去データ（またはダミーデータ）に基づいた戦略検証が可能。
- **Notification**: Discord Webhookによる通知機能。

## 必要要件
- Python 3.10+
- OANDA API Access Token (本番運用時)

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/tndhk/No30_fx1.git
cd No30_fx1

# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate

# 依存ライブラリのインストール
pip install -r requirements.txt
```

## 設定

`.env.example` を `.env` にコピーし、必要事項を入力してください。
Mock Modeで動かす場合は、APIトークンは空でも構いません。

```bash
cp .env.example .env
nano .env
```

```env
# .env
OANDA_ACCESS_TOKEN=your_token_here
OANDA_ACCOUNT_ID=your_account_id_here
OANDA_ENV=practice  # or live / mock
DISCORD_WEBHOOK_URL=your_discord_webhook_url
```

※ `OANDA_ENV` が設定されていない、またはトークンがない場合は自動的に Mock Mode で動作します。

## 使い方

### 1. 自動売買ボットの実行 (Mock Mode)
ダミーデータを生成し、移動平均線クロス戦略に基づいて模擬売買を行います。

```bash
python -m src.bot
```

### 2. バックテストの実行
ダミーデータ（ランダムウォーク）を生成し、戦略のパフォーマンスを検証します。

```bash
python run_backtest.py
```

### 3. データ取得 (要APIトークン)
OANDAからヒストリカルデータを取得し、SQLiteデータベース (`data/market_data.db`) に保存します。

```bash
python src/fetch_data.py
```

## ディレクトリ構成

- `src/`: ソースコード
    - `bot.py`: ボットのメインループ
    - `strategy.py`: 売買ロジック (SMAなど)
    - `backtest.py`: バックテストエンジン
    - `execution.py`: 注文執行 (Mock/Real)
    - `notification.py`: 通知 (Discord/Stdout)
    - `data_generator.py`: ダミーデータ生成
- `tests/`: テストコード
- `data/`: データ保存用 (SQLite)

## ライセンス
MIT
