# テストAPI開発

DynamoDBのテーブル設計を理解するためのバックエンドAPIを開発

## 構成

- Amazon Dynamo DB
- API Gateway
- Amazon Lambda

後日図を作成

## URL,クエリ設計

### URLテーブル

|  HTTP Verb  |  URL  |  クエリ説明  |
| ---- | ---- | ---- |
|  GET  |  /songs?artist_name={}  |  アーティスト名を指定して全ての曲を取得  |
|  GET  |  /albums?genre={}  |  ジャンルを指定してアルバム一覧を取得  |
|  GET  |  /songs?release={}&artist_name={} |  リリース年とアーティスト名から曲を取得  |
|  GET  |  /songs?name={}  |  指定した曲の名前を取得 |
|  PATCH  |  /songs/:id |  指定したidの曲を変更 |
|  PUT  |  /songs  |  曲を追加  |
|  DELETE  |  /songs/:id  |  指定したidの曲を削除  |

### クエリから必要の機能を洗い出し

- [ ] Artist名からSongを探す
- [x] Genreを指定してAlbumを探す
- [ ] Artist名もしくはReleaseからSongを探す

## DBのテーブル設計

### RDBMSテーブル設計図

<img src="https://user-images.githubusercontent.com/49640294/116804982-1c990d00-ab5e-11eb-915b-6d051bb7fe2b.png" width="45%" alt="MusicAPIテーブル">

### Artistテーブル

|ID|ArtistName|CareerSelect| |
|:----|:----|:----|:----|
|1|ずっと真夜中でいいのに。|2018| |
|2|RADWIMPS|2004| |
|3|YOASOBI|2019| |

### Songテーブル

|ID|SongTitle|Artist ID|Released|Alubum ID|
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

### 隣接関係のリスト設計パターン

#### テーブル

|Partition key(GSI1のSK)|Sort key(GSI1のPK,GSI2のPK)|Data|Career Start|
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
|Artist-1|Artist-1| |2018|
|Artist-2|Artist-2| |2004|
|Artist-2|Artist-2| |2019|

#### 用語

- GSI：Global Secondary Index
- LSI：Local Secondary Index

#### 設計のコツ

1. RDBMSにおいて、最も重要そうなエンティティのPrimary Key(エンティティのID)をPartition Keyに設定
   - Primary Keyに関係あるエンティティの外部キーをSort Keyに追加
   - こうすることでをアソシエーションを実現し、検索を高速化できる
2. 必要なクエリを洗い出す
   - クエリに引っ掛かる用語が含まれているエンティティをPartition Keyに
   - {エンティティ名}_{カラム名}をSort Keyに
   - Dataというカラムを作成し、Sort Keyに入れたカラムの値を入れる
   - Sort KeyをPartition Keyに、Partition KeyをSort KeyにしたGSIを導入することで、検索を高速化できる(GSI1)
3. 残りのカラムはエンティティIDをPartition KeyとSort Keyに入れる
   - Sort KeyをPartition KeyにしたGSIを導入することで、検索を高速化(GSI2)
4. その他、必要に応じて、LSIとGSIを使い、検索を高速化する

## 参考サイト

> AWS スライド  
> <https://www.slideshare.net/AmazonWebServicesJapan/db-20190905>  
> ブログ記事  
> <https://mizumotok.hatenablog.jp/entry/2019/08/14/175525>
