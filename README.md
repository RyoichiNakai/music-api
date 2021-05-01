# 音楽アプリのバックエンドAPI

## 構成

- Amazon Dynamo DB
- API Gateway
- Amazon Lambda
- ElastiCache

後日図を作成

## URLテーブル

  |  HTTP Verb  |  URL  |  用途  |
  | ---- | ---- | ---- |
  |  GET  |  /blog/articles  |  アーティスト名を指定して全ての曲を見つける  |
  |  GET  |  /blog/articles/  |  ジャンルを指定して全てのアルバムを見つける  |
  |  GET  |  /blog/  |  リリース年とアーティスト名から曲を検索する  |
  |  GET  |  /blog/  |  全探索  |
  |  PATCH  |  /blog/  |    |
  |  PUT  |  /blog/  |    |
  |  DELETE  |  /blog/  |    |

## pymemcache操作

### set

- メソッド

```python
set(key, value, expire=0, noreply=None, flags=None)
```

- パラメータ
  - key：str
  - value：str
  - expire：オプションのint型．キャッシュからvalueが削除されるまでの秒数．削除されない場合は0．
  - noreply：オプションのbool型，返事を待たない場合は True (デフォルトは self.default_noreply)
  - flags：オプションのint型，サーバー固有のフラグに使われる任意のビットフィールド．
- 戻り値
  - 例外が発生しない場合は，常にTrueを返す．
  - 例外が発生した場合は，setができたかを返す
  - noreplyがTrueの場合．setの成功は保証されない。

### get

- メソッド

```python
get(key, default=None)
```

1つのキーに対してのみ使用.

- パラメータ
  - key：str
  - default：keyが見つからなかった場合に返される値

- 戻り値
  - keyに対してのvalue
  - keyが見つからなかった場合はdefault

### get_many

- メソッド

```python
get_many(keys)
```

- パラメータ
  - keys：List(str)

- 戻り値
  - 引数はリストで、値はキャッシュから辞書型で返される

### gets

- メソッド

```python
gets(key, default=None, cas_default=None)
```

- パラメータ
  - key：str
  - default：keyが見つからなかった場合に返される値
  - cas_default：defaultと同じ

- 戻り値
  - (value, cas)のタプル
  - keyが見つからない場合は(default, cas_defaults)のタプル
