# DynamoDBにて簡単なバックエンドAPIを作成

## 構成

- Amazon Dynamo DB
- API Gateway
- Amazon Lambda
- ElastiCache

後日図を作成

## URLテーブル

  |  HTTP Verb  |  Path  |  Controller#Action  |
  | ---- | ---- | ---- |
  |  GET  |  /blog/articles(.:format)  |  blog/articles#index  |
  |  POST  |  /blog/articles(.:format)  |  blog/articles#create  |
  |  GET  |  /blog/articles/new(.:format)  |  blog/articles#new  |
  |  GET  |  /blog/articles/:id/edit(.:format)  |  blog/articles#edit  |
  |  GET  |  /blog/articles/:id(.:format)  |  blog/articles#show  |
  |  PATCH  |  /blog/articles/:id(.:format)  |  blog/articles#update  |
  |  PUT  |  /blog/articles/:id(.:format)  |  blog/articles#update  |
  |  DELETE  |  /blog/articles/:id(.:format)  |  blog/articles#destroy  |
