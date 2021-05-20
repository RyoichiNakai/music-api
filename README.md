# テストAPI開発

DynamoDBのテーブル設計を理解するためのバックエンドAPIを開発

## 構成

<div align="center">
  <img src="https://user-images.githubusercontent.com/49640294/118919794-2c8f5a00-b970-11eb-8fb5-2e585c21014e.png" alt="構成図">
</div>

## RDBのテーブル設計

### ER図

<img src="https://user-images.githubusercontent.com/49640294/116804982-1c990d00-ab5e-11eb-915b-6d051bb7fe2b.png" width="50%" alt="MusicAPIテーブル">

### Artistテーブル

|ID|ArtistName|CareerSelect|
|:----|:----|:----|
|1|ずっと真夜中でいいのに。|2018|
|2|RADWIMPS|2004|
|3|YOASOBI|2019|

### Songテーブル

|ID|SongName|Artist ID|Released|Alubum ID|
|:----|:----|:----|:----|:----|
|1|Ham|1|2020|1|
|2|サターン|1|2018|2|
|3|夜に駆ける|2|2019|3|
|4|君と羊と青|3|2011|4|
|5|ふたりごと|3|2006|5|
|6|有心論|3|2006|5|

### Albumテーブル

|ID|AlbumTitle|Artist ID|Genre|
|:----|:----|:----|:----|
|1|朗らかな皮膚とて不服|1|邦ロック|
|2|正しい偽りからの起床|1|邦ロック|
|3|THE BOOK|2|J-POP|
|4|絶体絶命|3|邦ロック|
|5|おかずのご飯|3|邦ロック|

## URL,クエリ設計

### URLテーブル

今回のテストAPIに必要なURLは以下のものとする。

|HTTP Verb|URL|クエリ説明|備考|
|----|----|----|----|
|GET|/songs?artist_name={}|アーティスト名を指定して全ての曲を取得|【追記】実行時間：約300ms|
|GET|/albums?genre={}|ジャンルを指定してアルバム一覧を取得|【追記】実行時間：約120ms|
|GET|/songs?release={}&artist_name={}|リリース年とアーティスト名から曲を取得|【追記】実行時間：約310ms|
|GET|/songs?name={}|指定した曲の名前を取得|
|PATCH|/songs/:id|指定したidの曲を変更|実装なし|
|POST|/songs|曲を追加|
|POST|/albums|アルバムを追加|
|POST|/artists|アーティストを追加|
|DELETE|/songs/:id|指定したidの曲を削除|実装なし|

### クエリから必要な機能を洗い出す

- [x] `ArtistName`から`SongName`を探す
- [x] `Album`の`Genre`を指定し、それに関連した`AlbumName`を探す
- [x] `ArtistName`と`Song`の`Released`から`SongName`を探す

## DynamoDBのテーブル設計

### 隣接関係のリスト設計パターン

- RDBのテーブルをDynamoDBのテーブル用に`1つ`のテーブルに設計しなおす手法
  - RDBの`テーブルごとの主キー`をDynamo DBの`PK（Partition Key）`に設定
  - URL設計、クエリ設計から今回のAPI実装に必要なRDBのカラムを`SK（Sort Key）`に設定

- こうすることで、DBにインデックスを貼りやすい形式になり、検索を高速化することができる
  - Dynamo DBのインデックスは`GSI（Global Secondary Index）`と`LSI（Local Secondary Index）`が存在
  - `GSI`は`PK以外のキー`を`PK`にして`SK以外のキー`を`SK`にしてテーブルを作成しなおすインデックス
  - `LSI`は`PK`はそのまま、`SK以外のキー`を`SK`にしてテーブルを作成しなおすインデックス

  > DynamoDB設計のベストプラクティス
  > <https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/bp-general-nosql-design.html>

  > インデックスとは？  
  > <https://qiita.com/towtow/items/4089dad004b7c25985e3>

  > セカンダリインデックスとは？  
  > <https://qiita.com/shibataka000/items/e3f3792201d6fcc397fd>

### 1. リレーションをテーブルのレコード（１列）に保存

- テーブルの依存関係
  - `Artist`の子に`Song`と`Album`
  - `Album`の子に`Song`

- テーブルごとの重要度を依存関係で比較
  - 全ての親テーブルとなっている`Artist`を`PK`に
  - `Album`と`Song`に関しては、`Album`を`PK`に
  - と言いつつも、この部分に関しては、`PK'と`SK`に関しては、どっちがどっちでも特に問題はないと思う

- 今回のクエリ設計では`Album`から`Song`を探したり、`Song`から`Album`を検索することはないので、`Album`と`Song`レコードに保存しない
  - 後々のことを考えると、保存しといた方がいいかも
  - 追加しても、してなくてもそこまで変わらないので、今回はなしで

- テーブル

  |Partition key (GSI1のSK)|Sort key (GSIのPK)|
  |:----|:----|
  |`Artist-1`|`Song-1`|
  |`Artist-1`|`Song-2`|
  |`Artist-1`|`Album-1`|
  |`Artist-1`|`Album-2`|
  |`Artist-2`|`Song-3`|
  |`Artist-2`|`Album-3`|
  |`Artist-3`|`Song-4`|
  |`Artist-3`|`Song-5`|
  |`Artist-3`|`Song-6`|
  |`Artist-3`|`Album-4`|
  |`Artist-3`|`Album-5`|

<br/>

- 設計概要

  - 例えば、その`Artist`に関連する`Song`を全て持ってくることができる

  - 逆も然りで、`Song`から`Artist`を持ってくることもできる

  - リレーションを実装する際は、`SK`を`PK`にした、GSIを貼ることで通常時よりも検索を高速化することができる（`GSI1`）

  - それぞれのIDに関しては、UUIDか連番をもちいればOK
    - 今回の実装ではUUIDを採用

  - 各テーブルの詳細情報は、次のステップで設計

### 2. クエリ設計から必要なものを考える

- 今回のクエリ設計に引っかかるカラム名を考える
  - `Artist`テーブル
    - `ArtistName`
  - `Song`テーブル
    - `Released`
    - `SongName`
  - `Album`テーブル
    - `Genre`
    - `AlbumName`

- 結果として返して欲しいカラム
  - `SongName`
  - `AlbumName`

- 返して欲しいカラムを見つけるために使うカラム
  - `SongName`
    - `Released`
    - `ArtistName`

  - `AlbumName`
    - `Genre`

- このことから以下のようにテーブルを設計

  |Partition key (GSI1のSK)|Sort key (GSI1, GSI2のPK)|Data (GSI2のSK)|
  |:----|:----|:----|
  |Artist-1|Song-1| |
  |Artist-1|Song-2| |
  |Artist-1|Album-1| |
  |Artist-1|Album-2| |
  |Artist-2|Song-3| |
  |Artist-2|Album-3| |
  |Artist-3|Song-4| |
  |Artist-3|Song-5| |
  |Artist-3|Song-6| |
  |Artist-3|Album-4| |
  |Artist-3|Album-5| |
  |`Artist-1`|`Artist_Name`|`ずっと真夜中でいいのに。`|
  |`Artist-2`|`Artist_Name`|`RADWIMPS`|
  |`Artist-3`|`Artist_Name`|`YOASOBI`|
  |`Song-1`|`Song_Name`|`Ham`|
  |`Song-2`|`Song_Name`|`サターン`|
  |`Song-3`|`Song_Name`|`夜に駆ける`|
  |`Song-4`|`Song_Name`|`君と羊と青`|
  |`Song-5`|`Song_Name`|`ふたりごと`|
  |`Song-6`|`Song_Name`|`有心論`|
  |`Song-1`|`Song_ArtistName`|`ずっと真夜中でいいのに。`|
  |`Song-2`|`Song_ArtistName`|`ずっと真夜中でいいのに。`|
  |`Song-3`|`Song_ArtistName`|`YOASOBI`|
  |`Song-4`|`Song_ArtistName`|`RADWIMPS`|
  |`Song-5`|`Song_ArtistName`|`RADWIMPS`|
  |`Song-6`|`Song_ArtistName`|`RADWIMPS`|
  |`Song-1`|`Song_Release`|`2020`|
  |`Song-2`|`Song_Release`|`2018`|
  |`Song-3`|`Song_Release`|`2019`|
  |`Song-4`|`Song_Release`|`2011`|
  |`Song-5`|`Song_Release`|`2006`|
  |`Song-6`|`Song_Release`|`2006`|
  |`Album-1`|`Album_Name`|`朗らかな皮膚とて不服`|
  |`Album-2`|`Album_Name`|`正しい偽りからの起床`|
  |`Album-3`|`Album_Name`|`THE BOOK`|
  |`Album-4`|`Album_Name`|`絶体絶命`|
  |`Album-5`|`Album_Name`|`おかずのご飯`|
  |`Album-1`|`Album_Genre`|`邦ロック`|
  |`Album-2`|`Album_Genre`|`邦ロック`|
  |`Album-3`|`Album_Genre`|`J-POP`|
  |`Album-4`|`Album_Genre`|`邦ロック`|
  |`Album-5`|`Album_Genre`|`邦ロック`|

<br>

- 設計概要
  - `PK`は各テーブルの`主キー`とする
  - `SK`は`{テーブル名}_{カラム名}`という形にする
  - 新しく`Data`というカラムを追加し、その中に必要なデータを保存
  - `SK`を`PK`に、`Data`を`SK`としたGSIを張る（`GSI2`）
    - こうすることで、リクエストパラメータの値をそのまま検索にかけることができ、検索を高速化することができる

- 検索例
  - `Album`の`Genre`から`Album`の`Name`を探す
    - `GSI2`を使用して、`PK`の値を`Album_Name`、`SK`を`J-POP`にしたクエリをDynamoDBに投げる
    - DynamoDBから連想配列で以下の結果が返ってくる

    ```json
    [{
      "Partition Key": "Album-3",
      "Sort key": "Album_Name",
      "Data": "J-POP"
    }]
    ```

    - この結果の`Partiion Key`の部分を使用して、`GSI1`で`PK`の値を`Sort Key`、SKの値は`Album-3`としたクエリをDynamoDBに投げると、`THE BOOK`というアルバム名を取得できる

- 複合キーについて
  - 今回のテーブル設計には記載していないが、複数のリクエストパラメータを使用したAPIを実装した際は、`SK`に複合キーを追加しておくのがベター
  - `SK`を`{テーブル名}_{カラム1}_{カラム2}`としておく
    - 例：Song_ArtistName_Release
  - `Data`を`{カラム1の値}_{カラム2の値}`としておく
    - 例： YOASOBI_2019
  - 返ってきた値をフロントエンドで調整
  - こうしないと、バックエンドの実装がしんどくなる
  - 複数回、探索をしないといけなくなるので、遅延が大きく生じる
  - 結果、いいことがない

### 3. 使用していないカラムを追加していく

- ここまでで使用していないカラム
  - `Artist`の`Career Start`
  - そこまで頻繁に使うことがないだろうが、一応データを保存しておきたい

- この場合は`PK`と`SK`をともに`{テーブル名}-{ID}`とする
  - 新しく`Career Start`というカラムを追加
  - 以下のようにテーブルを設計する

  |Partition key (GSI1のSK)|Sort key (GSI1,GSI2のPK)|Data (GSI2のSK)|Career Start|
  |:----|:----|:----|:----|
  |Artist-1|Song-1| | |
  |Artist-1|Song-2| | |
  |Artist-1|Album-1| | |
  |Artist-1|Album-2| | |
  |Artist-2|Song-3| | |
  |Artist-2|Album-3| | |
  |Artist-3|Song-4| | |
  |Artist-3|Song-5| | |
  |Artist-3|Song-6| | |
  |Artist-3|Album-4| | |
  |Artist-3|Album-5| | |
  |Artist-1|Artist_Name|ずっと真夜中でいいのに。| |
  |Artist-2|Artist_Name|RADWIMPS| |
  |Artist-3|Artist_Name|YOASOBI| |
  |Song-1|Song_Name|Ham| |
  |Song-2|Song_Name|サターン| |
  |Song-3|Song_Name|夜に駆ける| |
  |Song-4|Song_Name|君と羊と青| |
  |Song-5|Song_Name|ふたりごと| |
  |Song-6|Song_Name|有心論| |
  |Song-1|Song_ArtistName|ずっと真夜中でいいのに。| |
  |Song-2|Song_ArtistName|ずっと真夜中でいいのに。| |
  |Song-3|Song_ArtistName|YOASOBI| |
  |Song-4|Song_ArtistName|RADWIMPS| |
  |Song-5|Song_ArtistName|RADWIMPS| |
  |Song-6|Song_ArtistName|RADWIMPS| |
  |Song-1|Song_Release|2020| |
  |Song-2|Song_Release|2018| |
  |Song-3|Song_Release|2019| |
  |Song-4|Song_Release|2011| |
  |Song-5|Song_Release|2006| |
  |Song-6|Song_Release|2006| |
  |Album-1|Album_Name|朗らかな皮膚とて不服| |
  |Album-2|Album_Name|正しい偽りからの起床| |
  |Album-3|Album_Name|THE BOOK| |
  |Album-4|Album_Name|絶体絶命| |
  |Album-5|Album_Name|おかずのご飯| |
  |Album-1|Album_Genre|邦ロック| |
  |Album-2|Album_Genre|邦ロック| |
  |Album-3|Album_Genre|J-POP| |
  |Album-4|Album_Genre|邦ロック| |
  |Album-5|Album_Genre|邦ロック| |
  |`Artist-1`|`Artist-1`| |`2018`|
  |`Artist-2`|`Artist-2`| |`2004`|
  |`Artist-2`|`Artist-2`| |`2019`|

### 4. その他、必要に応じて、LSIとGSIを使い、検索を高速化する

- 必要に応じてテーブル数を増やしたりすることも考える
- RDBの柔軟で綺麗なクエリ設計とは違い、速さが全てという思考に切り替えることが大事

## 注意書き

- ジャンル別のアルバムを取得する際のインデックスについて
  - `Album_Genre`から`Album-id`を`GSI2`を使用して、取得
  - その後、`Album-id` から `Album_Name`を`GSI1`を使用するのと使用しないで、取得に`約600ms`の遅延が生じる
  - 検索の掛け方に関しては、2の検索例に詳細を記載

## 参考サイト

> AWS スライド  
> <https://www.slideshare.net/AmazonWebServicesJapan/db-20190905>

> ブログ記事  
> <https://mizumotok.hatenablog.jp/entry/2019/08/14/175525>
