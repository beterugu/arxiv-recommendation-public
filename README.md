# arXiv Recommendation Public Dataset

図面判読 AI、BIM/CIM、製造業応用、土木インフラ、AI 活用ノウハウに寄せて収集・要約した arXiv 論文データの公開配布リポジトリです。

データは private 運用リポジトリから公開可能なフィールドだけを許可リスト方式で export しています。API key、処理済み ID、内部 workflow、private repo のコードは含みません。

## Static JSON API

GitHub Pages から認証なしで取得できます。

- `https://beterugu.github.io/arxiv-recommendation-public/api/metadata.json`
- `https://beterugu.github.io/arxiv-recommendation-public/api/latest.json`
- `https://beterugu.github.io/arxiv-recommendation-public/api/all_papers.json`
- `https://beterugu.github.io/arxiv-recommendation-public/api/schema.json`

## MCP Server

AI エージェントから使いやすいように、GitHub Pages の JSON を読む stdio MCP サーバーを同梱しています。

```bash
uvx --from git+https://github.com/beterugu/arxiv-recommendation-public arxiv-recommendation-mcp
```

### MCP config example

```json
{
  "mcpServers": {
    "arxiv-recommendation": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/beterugu/arxiv-recommendation-public",
        "arxiv-recommendation-mcp"
      ]
    }
  }
}
```

### Tools

- `get_metadata`: 公開データセットの件数、生成時刻、ファイル情報を返す
- `latest_papers`: 最新日次データを返す
- `search_papers`: タイトル、要旨、要約、タグ、応用アイデアをキーワード検索する
- `get_paper`: `arxiv_id` で 1 件取得する
- `recommend_papers_for_usecase`: ユースケース文から関連論文を推薦する

## Local development

```bash
python -m pip install -e .
arxiv-recommendation-mcp
```

別の API base URL を使う場合は `ARXIV_RECOMMENDATION_API_BASE_URL` を設定します。

```bash
export ARXIV_RECOMMENDATION_API_BASE_URL="https://example.com/api"
```
